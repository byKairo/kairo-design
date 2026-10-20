#!/usr/bin/env python3
"""Validate the catalog, route isolation, chapter anchors and local links."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from load_style import indexes,load,read_section,MODES

LINK = re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
SHARED = {'references/style-catalog.md','references/reliable-delivery.md',
          'references/platform-specs.md','references/platform-presets.json','catalog.json'}

def route_of(path,root):
    parts = path.relative_to(root).parts
    if len(parts)>=3 and parts[0]=='routes':
        return parts[1]
    if len(parts)==3 and parts[0]=='styles' and path.stem in MODES:
        return path.stem
    return None

def validate(root):
    root = root.resolve()
    errors,notes = [],[]
    try:
        records = indexes(root)
    except (OSError,ValueError,TypeError,KeyError) as error:
        return [str(error)],notes
    names = {}
    catalog_text = (root/'references/style-catalog.md').read_text()
    expected_files = set()
    for sid,record in records.items():
        try:
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',sid):
                raise ValueError('invalid ID')
            if set(record)!={'id','name','identity','family','parent_style','aliases','routes'}:
                raise ValueError('invalid catalog fields')
            if not all(isinstance(record[key],str) and record[key].strip() for key in ('id','name','identity','family')):
                raise ValueError('missing identity field')
            if not isinstance(record['aliases'],list) or not all(isinstance(s,str) and s.strip() for s in record['aliases']):
                raise ValueError('invalid aliases')
            for token in [sid,record['name'],*record['aliases']]:
                token=token.strip().casefold()
                if names.setdefault(token,sid)!=sid:
                    raise ValueError('alias collision: '+token)
            if set(record['routes'])!=set(MODES):
                raise ValueError('both routes must be declared')
            if f'`{sid}`' not in catalog_text:
                raise ValueError('missing from catalog menu')
            parent=record['parent_style']
            if parent is not None and (not isinstance(parent,str) or parent not in records or records[parent]['family']!=record['family']):
                raise ValueError('invalid parent or family')
            seen,node=set(),sid
            while node is not None:
                if node in seen:raise ValueError('parent cycle')
                seen.add(node);node=records[node]['parent_style']
            for mode in MODES:
                route=record['routes'][mode]
                if set(route)!={'status','style','meta'} or route['style']!=f'{mode}.md':
                    raise ValueError(f'{mode}: invalid route fields or path')
                path=root/'styles'/sid/route['style'];expected_files.add(path)
                if path.resolve()!=path or not path.read_text().strip():
                    raise ValueError(f'{mode}: empty or redirected style file')
                meta=route['meta']
                if not isinstance(meta,dict) or meta.get('mode')!=mode or meta.get('style_id')!=sid or meta.get('status')!=route['status']:
                    raise ValueError(f'{mode}: identity/status mismatch')
                allowed={'style_id','mode','status','uses','fits','avoid_for','keywords','risks',
                         'confusable_with','selection_basis','conditions','reason'}
                if set(meta)-allowed:raise ValueError(f'{mode}: unknown metadata fields')
                if route['status']=='unsupported':
                    if not meta.get('reason'):raise ValueError('unsupported route must state reason')
                    continue
                if route['status'] not in ('supported','conditional'):
                    raise ValueError('invalid status')
                if not isinstance(meta.get('selection_basis'),str) or not meta['selection_basis'].strip():
                    raise ValueError(f'{mode}: missing selection basis')
                for key in ('uses','fits','avoid_for','keywords','risks'):
                    if not isinstance(meta.get(key),list) or not all(isinstance(s,str) and s.strip() for s in meta[key]):
                        raise ValueError(f'{mode}: invalid {key}')
                if route['status']=='conditional' and not meta.get('conditions'):
                    raise ValueError(f'{mode}: conditional route lacks conditions')
                for other in meta.get('confusable_with',[]):
                    if other.get('id') not in records or other['id']==sid or not other.get('difference'):
                        raise ValueError(f'{mode}: invalid comparison')
                load(root,sid,mode)
            if sid=='editorial-design' and record['routes']['wordless']['status']!='conditional':
                raise ValueError('Editorial wordless route must retain its conditional keywords boundary')
        except (OSError,ValueError,TypeError,KeyError) as error:
            errors.append(f'{sid}: {error}')
    actual={p for p in (root/'styles').rglob('*') if p.is_file()}
    if actual!=expected_files:
        errors.append('style files do not match the declared catalog')
    for file in (root/'references').iterdir():
        if file.is_file() and str(file.relative_to(root)) not in SHARED:
            errors.append('unexpected shared document: '+file.name)
    for path in root.rglob('*.md'):
        mode=route_of(path,root);text=path.read_text()
        anchors=re.findall(r'<a id="([a-z-]+)"></a>',text)
        if len(anchors)!=len(set(anchors)):errors.append(f'{path.relative_to(root)}: duplicate chapter anchors')
        if mode:
            for anchor in anchors:
                try:read_section(root,mode,anchor)
                except (OSError,ValueError) as error:errors.append(str(error))
        for link in LINK.findall(text):
            target,_,anchor=link.strip().strip('<>').partition('#')
            if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:',target):continue
            dest=(path.parent/target).resolve() if target else path.resolve()
            if not dest.is_relative_to(root) or not dest.is_file():
                errors.append(f'{path.relative_to(root)}: broken/escaping link {link}');continue
            other=route_of(dest,root);relative=str(dest.relative_to(root))
            if anchor and dest.suffix=='.md' and f'<a id="{anchor}"></a>' not in dest.read_text():
                errors.append(f'{path.relative_to(root)}: unknown chapter anchor {link}')
            if mode:
                if other and other!=mode:errors.append(f'{path.relative_to(root)}: cross-route link {link}')
                elif other is None and relative not in SHARED and not relative.startswith('scripts/'):
                    errors.append(f'{path.relative_to(root)}: route exits into another design document {link}')
            elif str(path.relative_to(root)) in SHARED and other:
                errors.append(f'{path.relative_to(root)}: shared document loads route-specific design {link}')
    return errors,notes

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-root',type=Path,default=Path(__file__).resolve().parents[1])
    args=parser.parse_args();errors,notes=validate(args.skill_root)
    for error in errors:print('ERROR:',error)
    print(f'{len(errors)} errors; checks cover metadata and linked dependencies, not aesthetic quality or agent compliance.')
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
