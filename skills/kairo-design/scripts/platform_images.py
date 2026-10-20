#!/usr/bin/env python3
"""List platform presets; export without cropping or stretching; verify actual image files."""
from __future__ import annotations

import argparse
import io
import json
from fractions import Fraction
from pathlib import Path

MAX_PIXELS = 40_000_000

PRESETS = Path(__file__).resolve().parents[1] / 'references/platform-presets.json'
ALIASES = {'公众号': 'wechat', '微信公众号': 'wechat', '微信': 'wechat',
           '小红书': 'xiaohongshu', 'rednote': 'xiaohongshu', 'xhs': 'xiaohongshu',
           'twitter': 'x', '推特': 'x', '微信贴图': 'wechat-picture', '小绿书': 'wechat-picture', '普通配图': 'generic'}


def configuration():
    return json.loads(PRESETS.read_text(encoding='utf-8'))


def target(args):
    constraints = getattr(args, 'constraints_preset', None)
    if args.preset:
        if args.width is not None or args.height is not None or constraints:
            raise ValueError('Use a preset OR custom width and height.')
        profiles = configuration()['profiles']
        if args.preset not in profiles:
            raise ValueError('Unknown preset: ' + args.preset)
        return profiles[args.preset]
    if not args.width or not args.height or min(args.width, args.height) <= 0:
        raise ValueError('Provide --preset or positive --width and --height.')
    profile = {'width': args.width, 'height': args.height, 'formats': ['PNG', 'JPEG'],
               'max_bytes': None, 'note': 'Custom pixels; platform constraints not checked.'}
    if constraints:
        profiles = configuration()['profiles']
        if constraints not in profiles:
            raise ValueError('Unknown constraints preset: ' + constraints)
        reference = profiles[constraints]
        profile['formats'] = reference['formats']
        profile['max_bytes'] = reference['max_bytes']
        profile['aspect_ratio'] = reference['aspect_ratio']
        profile['constraints_preset'] = constraints
        profile['note'] = 'Custom pixels; format and recorded capacity constraints from ' + constraints + '. Check capacity_checked for availability.'
    return profile


def matches_ratio(width, height, ratio, policy="approximate"):
    """Default composition tolerance is 2%; strict requests retain exact equality."""
    left, right = ratio.split(':')
    a, b = Fraction(left), Fraction(right)
    if a <= 0 or b <= 0:
        raise ValueError('Aspect ratio components must be positive.')
    if policy not in {'approximate', 'strict'}:
        raise ValueError('ratio_policy must be approximate or strict.')
    actual, expected = Fraction(width, height), a / b
    return actual == expected if policy == 'strict' else abs(actual / expected - 1) <= Fraction(1, 50)


def effective_ratio(profile):
    policy = profile.get('ratio_policy', 'approximate')
    if policy not in {'approximate', 'strict'}:
        raise ValueError('ratio_policy must be approximate or strict.')
    # A tool fallback cannot override an explicitly strict request.
    return profile.get('aspect_ratio') if policy == 'strict' else profile.get('generation_aspect_ratio', profile.get('aspect_ratio'))


def pillow():
    try:
        from PIL import Image, ImageOps, ImageColor
    except ImportError as error:
        raise ValueError('Pillow is required; use the host-provided Python runtime or install it explicitly.') from error
    return Image, ImageOps, ImageColor


def guard_pixels(width, height):
    if width <= 0 or height <= 0 or width * height > MAX_PIXELS:
        raise ValueError(f'Image dimensions exceed the {MAX_PIXELS}-pixel safety limit.')


def open_image(path):
    Image, _, _ = pillow()
    try:
        source = Image.open(path)
    except Image.DecompressionBombError as error:
        raise ValueError('Image exceeds decoder pixel safety limit.') from error
    try:
        guard_pixels(*source.size)
    except ValueError:
        source.close()
        raise
    return source


def inspect(path, profile):
    Image, ImageOps, _ = pillow()
    with open_image(path) as source:
        guard_pixels(*source.size)
        source.load()
        size = source.size
        oriented_size = ImageOps.exif_transpose(source).size
        fmt = source.format
        animated = getattr(source, 'n_frames', 1) > 1
        orientation = source.getexif().get(274, 1)
        mode = source.mode
    byte_count = path.stat().st_size
    errors = []
    if profile.get('width') is not None and list(size) != [profile['width'], profile['height']]:
        errors.append('Actual pixels do not match target.')
    if profile.get('aspect_ratio') and not matches_ratio(*oriented_size, effective_ratio(profile), profile.get('ratio_policy', 'approximate')):
        errors.append('Actual aspect ratio does not match target; cropping and stretching are prohibited.')
    if orientation != 1 or oriented_size != size:
        errors.append('Normalize EXIF orientation before delivery.')
    if fmt not in profile['formats'] or animated:
        errors.append('Expected a static PNG or JPEG.')
    if mode not in {'RGB', 'RGBA', 'L', 'LA', 'P'}:
        errors.append('Normalize color mode through export before web delivery.')
    if profile.get('max_bytes') and byte_count > profile['max_bytes']:
        errors.append('File exceeds the verified platform size limit.')
    return {'path': str(path.resolve()), 'target': [profile.get('width'), profile.get('height')],
            'target_ratio': profile.get('aspect_ratio'),
            'generation_ratio': effective_ratio(profile),
            'ratio_policy': profile.get('ratio_policy', 'approximate'),
            'actual_ratio': oriented_size[0] / oriented_size[1],
            'ratio_relative_error': (abs(float(Fraction(*oriented_size) / (Fraction(effective_ratio(profile).split(':')[0]) / Fraction(effective_ratio(profile).split(':')[1]))) - 1) if effective_ratio(profile) else None),
            'actual': list(size), 'format': fmt, 'color_mode': mode, 'bytes': byte_count,
            'passed': not errors, 'errors': errors, 'note': profile['note'],
            'capacity_limit_bytes': profile.get('max_bytes'),
            'capacity_checked': profile.get('max_bytes') is not None}


def export(args, profile):
    Image, ImageOps, ImageColor = pillow()
    if args.output.exists():
        raise ValueError('Output already exists; choose a new filename.')
    fmt = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG'}.get(args.output.suffix.lower())
    if not fmt:
        raise ValueError('Output extension must be .png, .jpg or .jpeg.')
    if not 1 <= args.quality <= 95:
        raise ValueError('JPEG quality must be between 1 and 95.')
    if args.crop_box or args.allow_upscale:
        raise ValueError('Cropping and upscaling are not permitted.')
    if profile.get('width') is not None:
        guard_pixels(profile['width'], profile['height'])
    if fmt not in profile['formats']:
        raise ValueError('Output format is not allowed by the target profile.')
    with open_image(args.input) as source:
        guard_pixels(*source.size)
        if getattr(source, 'n_frames', 1) > 1:
            raise ValueError('Animated input is outside static-image delivery.')
        oriented = ImageOps.exif_transpose(source)
        im = oriented.convert('RGBA')
        # Normalize an embedded profile to sRGB before dropping metadata.
        if source.info.get('icc_profile'):
            from PIL import ImageCms
            alpha = im.getchannel('A')
            color_input = oriented if oriented.mode in {'RGB', 'CMYK', 'LAB', 'L'} else oriented.convert('RGB')
            try:
                im = ImageCms.profileToProfile(color_input,
                     ImageCms.ImageCmsProfile(io.BytesIO(source.info['icc_profile'])),
                     ImageCms.createProfile('sRGB'), outputMode='RGB').convert('RGBA')
            except ImageCms.PyCMSError as error:
                raise ValueError('Embedded ICC profile is incompatible with the image color mode.') from error
            im.putalpha(alpha)
    w, h = profile.get('width', im.width), profile.get('height', im.height)
    if profile.get('aspect_ratio') and not matches_ratio(im.width, im.height, effective_ratio(profile), profile.get('ratio_policy', 'approximate')):
        raise ValueError('Source aspect ratio does not match preset; regenerate at the requested ratio.')
    if w * im.height != h * im.width:
        raise ValueError('Aspect mismatch: cropping and stretching are prohibited.')
    scale = w / im.width
    if scale > 1:
        raise ValueError('Upscaling is not permitted; use a suitable native generation.')
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    if fmt == 'JPEG':
        if im.getchannel('A').getextrema()[0] < 255 and not args.background:
            raise ValueError('Transparent JPEG export requires an explicit --background.')
        rgba = ImageColor.getcolor(args.background or '#ffffff', 'RGBA')
        if rgba[3] != 255:
            raise ValueError('JPEG background must be fully opaque.')
        background = Image.new('RGBA', im.size, rgba)
        background.alpha_composite(im)
        im = background.convert('RGB')
    output = io.BytesIO()
    im.save(output, format=fmt, **({'quality': args.quality, 'optimize': True} if fmt == 'JPEG' else {}))
    payload = output.getvalue()
    if profile.get('max_bytes') and len(payload) > profile['max_bytes']:
        raise ValueError('Export exceeds platform limit; lower JPEG quality or revise export.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as handle:
        handle.write(payload)
    result = inspect(args.output, profile)
    result['upscaled'] = scale > 1
    result['crop_box'] = args.crop_box
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    presets = sub.add_parser('presets')
    presets.add_argument('--platform', action='append')
    for command in ('check', 'export'):
        p = sub.add_parser(command)
        p.add_argument('--input', type=Path, required=True)
        p.add_argument('--preset')
        p.add_argument('--strict-ratio', action='store_true', help='Require mathematically exact ratio only when explicitly requested.')
        p.add_argument('--width', type=int)
        p.add_argument('--height', type=int)
        p.add_argument('--constraints-preset', help='Apply format and capacity constraints to custom pixels.')
        if command == 'export':
            p.add_argument('--output', type=Path, required=True)
            p.add_argument('--crop-box', type=int, nargs=4)
            p.add_argument('--allow-upscale', action='store_true')
            p.add_argument('--background')
            p.add_argument('--quality', type=int, default=92)
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            import sys
            pillow()
            import PIL
            from PIL import ImageCms
            ImageCms.createProfile('sRGB')
            result = {'passed': True, 'python': sys.executable, 'pillow': PIL.__version__, 'color_management': True}
        elif args.command == 'presets':
            config = configuration()
            selected = [ALIASES.get(x.lower(), x.lower()) for x in (args.platform or config['defaults'])]
            if any(x not in config['defaults'] for x in selected):
                raise ValueError('Unknown platform; choose wechat, wechat-picture, xiaohongshu, x or generic.')
            result = {'checked_on': config['checked_on'],
                      'defaults': {x: config['defaults'][x] for x in selected},
                      'profiles': {k: v for k, v in config['profiles'].items() if v['platform'] in selected}}
        else:
            profile = dict(target(args))
            if args.strict_ratio:
                profile['ratio_policy'] = 'strict'
            result = inspect(args.input, profile) if args.command == 'check' else export(args, profile)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('passed', True) else 1
    except (ValueError, OSError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
