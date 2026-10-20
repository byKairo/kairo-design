#!/usr/bin/env python3
"""Load one style route or one design chapter without exposing other routes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

MODES = ('with-text', 'wordless')

def indexes(root: Path) -> dict[str, dict]:
    document = json.loads((root/'catalog.json').read_text(encoding='utf-8'))
    if document.get('version') != 1 or not isinstance(document.get('styles'),list):
        raise ValueError('invalid catalog schema')
    records = {}
    for record in document['styles']:
        if not isinstance(record,dict) or not isinstance(record.get('id'),str) or not record['id']:
            raise ValueError('missing style identity')
        if record['id'] in records:
            raise ValueError('duplicate style identity: '+record['id'])
        records[record['id']] = record
    if not records:
        raise ValueError('no style identities')
    return records

def resolve(records: dict[str,dict], query: str) -> str:
    query = query.strip().casefold()
    matches = [sid for sid,rec in records.items()
               if query in [s.strip().casefold() for s in [sid,rec['name'],*rec['aliases']]]]
    if len(matches) != 1:
        raise ValueError('unknown or ambiguous style name: '+query)
    return matches[0]

def load(root: Path, query: str, mode: str) -> dict:
    root = root.resolve()
    if mode not in MODES:
        raise ValueError('explicit mode must be with-text or wordless')
    if query.strip().casefold() in ('paper-surface-relief', '纸面压凹浮凸', '纸面压印'):
        if mode != 'with-text':
            raise ValueError('Legacy paper finish is documented only for with-text; do not import it into wordless.')
        return {'selected': 'paper-surface-relief', 'mode': mode, 'kind': 'technique',
                'styles': [], 'technique': read_section(root, mode, 'paper-finishes')}
    records = indexes(root)
    selected = resolve(records,query)
    chain,seen = [],set()
    def visit(sid):
        if sid in seen:
            raise ValueError('parent cycle: '+sid)
        if sid not in records:
            raise ValueError('missing parent: '+sid)
        seen.add(sid)
        record = records[sid]
        route = record['routes'][mode]
        if route['status']=='unsupported':
            raise ValueError(f'{sid}: {mode} is unsupported; choose a compatible style')
        if route['status'] not in ('supported','conditional'):
            raise ValueError('invalid route status')
        parent = record.get('parent_style')
        if parent:
            visit(parent)
        expected = root/'styles'/sid/f'{mode}.md'
        path = root/'styles'/sid/route['style']
        if path.resolve()!=expected or not path.resolve().is_relative_to(root):
            raise ValueError(f'{sid}: {mode} style must stay in its own route')
        meta = route['meta']
        if not isinstance(meta,dict) or meta.get('mode')!=mode or meta.get('style_id')!=sid or meta.get('status')!=route['status']:
            raise ValueError(f'{sid}: route metadata mismatch')
        chain.append({'id':sid,'name':record['name'],'identity':record['identity'],'mode':mode,
                      'meta_path':str(root/'catalog.json'),'style_path':str(path),
                      'meta':meta,'style':path.read_text(encoding='utf-8')})
    visit(selected)
    return {'selected':selected,'mode':mode,'styles':chain}

def read_section(root: Path, mode: str, section: str) -> dict:
    root = root.resolve()
    if mode not in MODES or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*',section):
        raise ValueError('invalid route or chapter')
    file = 'design-guide.md' if mode=='with-text' and section!='workflow' else 'WORKFLOW.md'
    path = root/'routes'/mode/file
    text = path.read_text(encoding='utf-8')
    if not(mode=='with-text' and section=='workflow'):
        markers = list(re.finditer(r'<a id="([a-z-]+)"></a>',text))
        found = [i for i,m in enumerate(markers) if m.group(1)==section]
        if len(found)!=1:
            raise ValueError('unknown or ambiguous design chapter: '+section)
        i = found[0]
        text = text[markers[i].end():markers[i+1].start() if i+1<len(markers) else len(text)].strip()
    return {'mode':mode,'section':section,'path':str(path),'text':text}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--style')
    choice.add_argument('--section',help='Read one named design chapter, such as image-brief or quality-check.')
    parser.add_argument('--mode',required=True,choices=MODES)
    parser.add_argument('--skill-root',type=Path,default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = load(args.skill_root,args.style,args.mode) if args.style is not None else read_section(args.skill_root,args.mode,args.section)
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(1,f'ERROR: {error}\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
