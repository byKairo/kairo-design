#!/usr/bin/env python3
"""Verify final files against an explicit brief and hash-bound visual review.

This checks review completeness and file invariants, not visual truth.
"""
import argparse
import hashlib
import json
import unicodedata
from pathlib import Path

from platform_images import inspect, guard_pixels, configuration, matches_ratio, effective_ratio
from reading_plan import required_readings, route_mode

CHECKS = ('text', 'content', 'action', 'style', 'readability', 'preservation')


def compact_lines(text):
    return text.replace('\r\n', '\n').replace('\n', '')


def semantic_text(text):
    return ''.join(c for c in text if not c.isspace() and not unicodedata.category(c).startswith('P'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(brief_path, review_path):
    brief = json.loads(brief_path.read_text(encoding='utf-8'))
    review = json.loads(review_path.read_text(encoding='utf-8'))
    errors = []
    if not isinstance(brief, dict) or not isinstance(review, dict):
        raise ValueError('Brief and review must be objects.')
    if review.get('brief_sha256') != digest(brief_path):
        errors.append('Brief changed or is not bound to this review.')
    targets, items = brief.get('targets'), review.get('items')
    if not isinstance(targets, list) or not targets or not isinstance(items, list):
        raise ValueError('Nonempty targets and an items list are required.')
    expected = {}
    for target in targets:
        if not isinstance(target, dict) or not isinstance(target.get('id'), str) or not target['id']:
            raise ValueError('Each target needs a nonempty string id.')
        if target['id'] in expected:
            raise ValueError('Duplicate target id.')
        if any(type(target.get(key)) is not int for key in ('width', 'height')):
            raise ValueError('Target width and height must be integers.')
        guard_pixels(target['width'], target['height'])
        if target.get('text_policy') not in ('exact', 'none', 'keywords', 'unspecified'):
            raise ValueError('Each target needs a text_policy.')
        if target['text_policy'] == 'exact' and not isinstance(target.get('locked_text'), str):
            raise ValueError('Exact text needs a locked_text string.')
        if not isinstance(target.get('style'), str) or not target['style']:
            raise ValueError('Each target needs its style or custom style identity.')
        preset = target.get('constraints_preset')
        if preset and preset not in configuration()['profiles']:
            raise ValueError('Unknown constraints preset.')
        ratio = target.get('aspect_ratio') or (configuration()['profiles'][preset]['aspect_ratio'] if preset else None)
        if not isinstance(ratio, str):
            raise ValueError('Target needs aspect_ratio or a known constraints_preset.')
        try:
            if not matches_ratio(target['width'], target['height'], effective_ratio(dict(target, aspect_ratio=ratio)), target.get('ratio_policy', 'approximate')):
                errors.append(f"{target['id']}: target pixels conflict with target ratio.")
        except (ValueError, ZeroDivisionError, TypeError):
            raise ValueError('Invalid positive aspect ratio.')
        route_mode(target)
        if 'title_text' in target:
            title = target['title_text']
            if not isinstance(title, str) or not title.strip():
                raise ValueError('title_text must be nonempty.')
            if target['text_policy'] != 'exact' or not isinstance(target.get('locked_text'), str) or compact_lines(title) not in compact_lines(target['locked_text']):
                errors.append(f"{target['id']}: complete title missing from all-text specification.")
        if target['text_policy'] == 'keywords':
            words, source = target.get('allowed_keywords'), target.get('source_title')
            if not isinstance(words, list) or not words or any(not isinstance(w, str) or not w.strip() for w in words):
                raise ValueError('Keywords require an explicit nonempty word list.')
            if not isinstance(source, str) or not semantic_text(source):
                raise ValueError('Keywords require the original or internally drafted source title.')
            origin = target.get('keyword_origin')
            if origin not in ('extracted', 'user'):
                raise ValueError('keyword_origin must be extracted or user.')
            if origin == 'extracted' and any(w not in source for w in words):
                errors.append(f"{target['id']}: extracted keywords are not in source title.")
            selected = ''.join(words)
            if len(semantic_text(selected)) >= len(semantic_text(source)):
                errors.append(f"{target['id']}: keywords must remain a short selection, not the full title.")
            if target.get('locked_text') != selected:
                errors.append(f"{target['id']}: keyword text differs from the exact allowed list.")
        if target.get('source_title') is not None and target['text_policy'] != 'keywords':
            original = target['source_title']
            title = target.get('title_text')
            if not isinstance(original, str) or not isinstance(title, str):
                raise ValueError('source_title and title_text must be strings.')
            if original != title:
                approval = target.get('title_change_approval')
                if not isinstance(approval, dict) or approval.get('approved') is not True or not isinstance(approval.get('evidence'), str) or not approval['evidence'].strip():
                    errors.append(f"{target['id']}: title change lacks recorded user approval.")
        expected[target['id']] = target
    delivered, files = set(), set()
    root = review_path.parent.resolve()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('Review items must be objects.')
        label = item.get('target_id')
        if not isinstance(label, str) or label not in expected or label in delivered:
            errors.append('Unknown or duplicate delivered target.')
            continue
        delivered.add(label)
        target = expected[label]
        readings = item.get('readings')
        needed = required_readings(target)
        if not isinstance(readings, list) or any(not isinstance(v, str) for v in readings):
            errors.append(f'{label}: actual reading record missing.')
        else:
            missing = sorted(set(needed) - set(readings))
            if missing:
                errors.append(f'{label}: missing required readings: ' + ', '.join(missing))
        relative = item.get('path')
        if not isinstance(relative, str) or Path(relative).is_absolute():
            errors.append(f'{label}: file path must be relative to review directory.')
            continue
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f'{label}: missing file or path outside review directory.')
            continue
        if path in files:
            errors.append(f'{label}: same file reused for multiple targets.')
        files.add(path)
        if item.get('sha256') != digest(path):
            errors.append(f'{label}: final file changed since visual review.')
        design = item.get('design_review')
        if not isinstance(design, dict):
            errors.append(f'{label}: design review missing.')
        else:
            if design.get('decision') not in ('retain', '保留'):
                errors.append(f'{label}: design is not retained for delivery.')
            if not isinstance(design.get('evidence'), str) or not design['evidence'].strip():
                errors.append(f'{label}: design review lacks visible evidence.')
            # False user_accepted also means pending, so it is not a veto.
            if design.get('user_feedback_status') == 'rejected':
                errors.append(f'{label}: user explicitly rejected the design.')
            if design.get('delivery_status') in ('rejected_not_final', 'rejected', 'failed', 'needs_revision'):
                errors.append(f'{label}: design is explicitly excluded from final delivery.')
        if item.get('delivery_status') in ('rejected_not_final', 'rejected', 'failed', 'needs_revision'):
            errors.append(f'{label}: item is explicitly excluded from final delivery.')
        checks = item.get('checks')
        if not isinstance(checks, dict):
            errors.append(f'{label}: visual checks missing.')
            continue
        for key in CHECKS:
            check = checks.get(key)
            allowed = {'pass'}
            if key == 'preservation' and not target.get('edit', False):
                allowed.add('not_applicable')
            if not isinstance(check, dict) or check.get('status') not in allowed or not isinstance(check.get('evidence'), str) or not check['evidence'].strip():
                errors.append(f'{label}: {key} has no passing review with evidence.')
        if target['text_policy'] in ('exact', 'keywords') and item.get('observed_text') != target['locked_text']:
            errors.append(f'{label}: observed text does not exactly match locked text.')
        if 'title_text' in target:
            if item.get('observed_title') != target['title_text']:
                errors.append(f'{label}: observed title differs from title_text.')
            observed = item.get('observed_text')
            if not isinstance(observed, str) or compact_lines(target['title_text']) not in compact_lines(observed):
                errors.append(f'{label}: observed title is missing from all observed text.')
        if target['text_policy'] == 'none' and item.get('observed_text') != '':
            errors.append(f'{label}: wordless image lacks an explicit empty-text observation.')
        profile = {'width': target['width'], 'height': target['height'],
                   'formats': ['PNG', 'JPEG'], 'max_bytes': None, 'note': 'Job specification.'}
        if target.get('aspect_ratio'):
            profile['aspect_ratio'] = target['aspect_ratio']
        # Known platform constraints come from trusted local presets, not the review.
        if target.get('constraints_preset'):
            presets = configuration()['profiles']
            if target['constraints_preset'] not in presets:
                raise ValueError('Unknown constraints preset.')
            reference = presets[target['constraints_preset']]
            profile.update(formats=reference['formats'], max_bytes=reference['max_bytes'])
            profile.setdefault('aspect_ratio', reference['aspect_ratio'])
        profile['ratio_policy'] = target.get('ratio_policy', 'approximate')
        if target.get('generation_aspect_ratio'):
            profile['generation_aspect_ratio'] = target['generation_aspect_ratio']
        result = inspect(path, profile)
        errors.extend(f'{label}: {error}' for error in result['errors'])
    if delivered != set(expected):
        errors.append('Delivered target count or identities do not match the brief.')
    return {'passed': not errors, 'errors': errors, 'expected_count': len(targets),
            'delivered_count': len(items), 'visual_truth_checked_by_script': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--brief', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.brief, args.review)
    except (ValueError, OSError, TypeError) as error:
        result = {'passed': False, 'error': str(error)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
