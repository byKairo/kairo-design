#!/usr/bin/env python3
"""Render exact, glyph-checked text on a reviewed normalized PNG, or plain canvas."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct

from platform_images import guard_pixels, open_image, pillow


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unicode_map(path, face):
    if path.stat().st_size > 64 * 1024 * 1024: raise ValueError('Font file exceeds the 64 MiB input limit.')
    data = path.read_bytes()
    def u16(offset): return struct.unpack_from('>H', data, offset)[0]
    def u32(offset): return struct.unpack_from('>I', data, offset)[0]
    if data[:4] == b'ttcf':
        if not 0 <= face < u32(8): raise ValueError('Font collection index is out of range.')
        sfnt = u32(12 + face * 4)
    else:
        if face != 0: raise ValueError('Single font requires font_index 0.')
        sfnt = 0
    cmap = None
    for index in range(u16(sfnt + 4)):
        table = sfnt + 12 + index * 16
        if data[table:table+4] == b'cmap': cmap = u32(table + 8)
    if cmap is None: raise ValueError('Font has no cmap table.')
    choices = []
    for index in range(u16(cmap + 2)):
        record = cmap + 4 + index * 8
        platform, encoding = u16(record), u16(record + 2)
        if platform != 0 and not (platform == 3 and encoding in (1, 10)): continue
        sub = cmap + u32(record + 4)
        fmt = u16(sub)
        if fmt in (4, 12): choices.append((fmt, platform == 3, sub))
    if not choices: raise ValueError('Font needs a Unicode cmap format 4 or 12.')
    # Select one subtable consistently; prefer supplementary coverage.
    fmt, _, sub = max(choices)
    glyphs = set()
    if fmt == 12:
        for index in range(u32(sub + 12)):
            start, end, glyph = struct.unpack_from('>III', data, sub + 16 + index * 12)
            if not 0 <= start <= end <= 0x10ffff: raise ValueError('Invalid font Unicode range.')
            glyphs.update(range(start + (glyph == 0), end + 1))
    else:
        segments = u16(sub + 6) // 2
        ends = sub + 14
        starts = ends + segments * 2 + 2
        deltas = starts + segments * 2
        ranges = deltas + segments * 2
        for index in range(segments):
            start, end = u16(starts + index * 2), u16(ends + index * 2)
            delta, offset = u16(deltas + index * 2), u16(ranges + index * 2)
            for codepoint in range(start, end + 1):
                if offset == 0: glyph = (codepoint + delta) & 0xffff
                else:
                    glyph = u16(ranges + index * 2 + offset + 2 * (codepoint - start))
                    if glyph: glyph = (glyph + delta) & 0xffff
                if glyph: glyphs.add(codepoint)
    return glyphs


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum: raise ValueError(name + ' must be an integer in range.')
    return value


def rectangle(value, width, height):
    if not isinstance(value, list) or len(value) != 4: raise ValueError('Box requires x, y, width, height.')
    x, y, w, h = [integer(v, 'box value') for v in value]
    if not w or not h or x+w > width or y+h > height: raise ValueError('Box exceeds canvas bounds.')
    return x, y, w, h


def render(spec_path, output, input_path=None):
    Image, _, ImageColor = pillow()
    from PIL import ImageDraw, ImageFont
    if output.exists(): raise ValueError('Output already exists; choose a new filename.')
    if output.suffix.lower() != '.png': raise ValueError('Typesetting output must be PNG; encode delivery formats through platform_images.py.')
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    if not isinstance(spec, dict): raise ValueError('Spec must be an object.')
    width, height = integer(spec.get('width'), 'width', 1), integer(spec.get('height'), 'height', 1)
    guard_pixels(width, height)
    if input_path:
        with open_image(input_path) as source:
            if source.size != (width, height) or source.getexif().get(274, 1) != 1 or source.mode not in ('RGB','RGBA') or getattr(source,'n_frames',1) != 1 or source.info.get('icc_profile'):
                raise ValueError('Normalize input size, orientation, mode and ICC through platform_images.py first.')
            image = source.convert('RGBA')
    else:
        image = Image.new('RGBA', (width, height), ImageColor.getcolor(spec.get('background','#ffffff'),'RGBA'))
    draw = ImageDraw.Draw(image)
    shapes = spec.get('rectangles', [])
    if not isinstance(shapes, list): raise ValueError('rectangles must be a list.')
    for shape in shapes:
        x,y,w,h = rectangle(shape['box'],width,height)
        draw.rectangle((x,y,x+w-1,y+h-1),fill=ImageColor.getcolor(shape['color'],'RGBA'))
    blocks, locked = spec.get('blocks'), spec.get('locked_texts')
    if not isinstance(blocks,list) or not blocks or not isinstance(locked,list): raise ValueError('blocks and locked_texts are required.')
    if any(not isinstance(block,dict) for block in blocks) or [block.get('text') for block in blocks] != locked:
        raise ValueError('Text blocks do not match locked_texts.')
    rows, occupied, fonts = [], [], {}
    for block in blocks:
        text, lines = block.get('text'), block.get('lines')
        joiner = block.get('line_joiner','')
        if not isinstance(text,str) or not text or not isinstance(lines,list) or not lines or any(not isinstance(line,str) or not line or '\n' in line or '\r' in line for line in lines):
            raise ValueError('Each text block needs nonempty text and lines.')
        if joiner not in ('','\n') or joiner.join(lines) != text: raise ValueError('Line grouping changes original text or punctuation.')
        font_path = Path(block['font']).expanduser()
        face = integer(block.get('font_index',0),'font_index')
        size = integer(block['font_size'],'font_size',1)
        if size > 2048: raise ValueError('Font size is too large.')
        key = (font_path.resolve(),face)
        if key not in fonts: fonts[key] = unicode_map(font_path,face)
        missing = [char for char in sorted(set(text.replace('\n',''))) if ord(char) not in fonts[key]]
        if missing: raise ValueError('Font lacks glyphs: ' + repr(''.join(missing)))
        font = ImageFont.truetype(str(font_path),size,index=face)
        x,y,w,h = rectangle(block['box'],width,height)
        step = integer(block.get('line_height',round(size*1.2)),'line_height',1)
        color = ImageColor.getcolor(block.get('color','#000000'),'RGBA')
        if color[3] != 255: raise ValueError('Reading text must use an opaque color.')
        for index,line in enumerate(lines):
            bounds = font.getbbox(line)
            ink_w, ink_h = bounds[2]-bounds[0], bounds[3]-bounds[1]
            top = y+index*step
            if ink_w > w or top+ink_h > y+h or (index < len(lines)-1 and ink_h > step):
                raise ValueError('Text exceeds box or line spacing; revise layout without changing locked text.')
            ink = (x,top,x+ink_w,top+ink_h)
            if not spec.get('allow_text_overlap',False) and any(ink[0]<other[2] and ink[2]>other[0] and ink[1]<other[3] and ink[3]>other[1] for other in occupied):
                raise ValueError('Text ink boxes overlap; revise layout.')
            occupied.append(ink)
            draw.text((x-bounds[0],top-bounds[1]),line,font=font,fill=color)
            rows.append({'text':line,'ink_box':ink,'font_identity':font.getname(),'font_sha256':digest(font_path),'font_index':face,'font_size':size})
    buffer = io.BytesIO(); image.save(buffer,format='PNG')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('xb') as handle: handle.write(buffer.getvalue())
    return {'passed':True,'path':str(output.resolve()),'sha256':digest(output),
            'spec_sha256':digest(spec_path),'input_sha256':digest(input_path) if input_path else None,
            'actual':[width,height],'locked_texts':locked,'rows':rows,'visual_review_complete':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,required=True)
    parser.add_argument('--input',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    try: result = render(args.spec,args.output,args.input)
    except (ValueError,OSError,KeyError,TypeError,struct.error) as error:
        result = {'passed':False,'error':str(error)}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
