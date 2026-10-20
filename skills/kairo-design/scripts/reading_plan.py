#!/usr/bin/env python3
"""Resolve required reading records. Completeness is not proof of reading or understanding."""
import argparse
import json
from pathlib import Path
from load_style import load, read_section, indexes, resolve

ROOT = Path(__file__).resolve().parents[1]
FEATURES = {'collage': 'collage-composition',
            'object_transformation': 'object-transformation',
            'paper_finishes': 'paper-finishes', 'exact_typography': 'exact-typography'}


def route_mode(target, root=ROOT):
    policy = target.get('text_policy')
    inferred = {'exact': 'with-text', 'none': 'wordless', 'keywords': 'wordless'}.get(policy)
    mode = target.get('mode', inferred)
    if mode not in ('with-text', 'wordless') or (inferred and inferred != mode):
        raise ValueError('Missing or conflicting route mode.')
    if mode == 'wordless' and policy not in ('none', 'keywords'):
        raise ValueError('Wordless route requires none or its restricted keywords exception.')
    if policy == 'keywords':
        if target.get('style_source') != 'catalog' or resolve(indexes(root), target.get('style', '')) != 'editorial-design':
            raise ValueError('Keywords exception is exclusive to editorial-design wordless route.')
    elif mode == 'wordless' and target.get('style_source') == 'catalog':
        if resolve(indexes(root), target.get('style', '')) == 'editorial-design':
            raise ValueError('Editorial wordless route requires keywords; use another style for strictly no text.')
    return mode


def required_readings(target, root=ROOT):
    mode = route_mode(target, root)
    source = target.get('style_source')
    if source not in ('catalog', 'custom', 'technique'):
        raise ValueError('style_source must be catalog, custom or technique.')
    features = target.get('design_features')
    if not isinstance(features, dict) or set(features) != set(FEATURES) or any(type(v) is not bool for v in features.values()):
        raise ValueError('design_features must explicitly assess all four boolean feature flags.')
    required = {'SKILL.md', 'references/platform-specs.md', 'references/reliable-delivery.md'}
    sections = ['workflow', 'art-direction', 'prompt-blueprint', 'quality-check']
    if mode == 'with-text':
        sections += ['image-brief', 'design-decisions', 'text-led-design', 'typography-and-layout',
                     'color-and-information', 'style-language', 'generation-review']
        sections += [section for feature, section in FEATURES.items() if features[feature]]
    if source in ('catalog', 'technique'):
        loaded = load(root, target['style'], mode)
        if (loaded.get('kind') == 'technique') != (source == 'technique'):
            raise ValueError('Style source does not match the resolved style or technique.')
        if source == 'technique':
            sections.append('paper-finishes')
        else:
            required.update(('catalog.json', 'references/style-catalog.md'))
            for entry in loaded['styles']:
                required.add(str(Path(entry['style_path']).relative_to(root)))
            if mode == 'with-text' and loaded['selected'] == 'torn-photo-collage':
                sections.append('collage-composition')
    for section in sections:
        data = read_section(root, mode, section)
        required.add(str(Path(data['path']).relative_to(root)) + '#' + section)
    for resource in required:
        if not (root / resource.split('#')[0]).is_file():
            raise ValueError('Required resource missing: ' + resource)
    return sorted(required)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True, help='One target object, not the entire brief.')
    args = parser.parse_args()
    try:
        result = {'required_readings': required_readings(json.loads(args.target.read_text()))}
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}, ensure_ascii=False)); return 1
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0

if __name__ == '__main__':
    raise SystemExit(main())
