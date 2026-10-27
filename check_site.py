"""Check generated routes, assets, anchors and publication boundaries."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'

class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs = []; self.ids = set(); self.title = False; self.lang = False
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs: self.ids.add(attrs['id'])
        if tag == 'title': self.title = True
        if tag == 'html' and attrs.get('lang'): self.lang = True
        if tag in ('a', 'link') and attrs.get('href'): self.refs.append((attrs['href'], tag))
        if tag in ('img', 'script') and attrs.get('src'): self.refs.append((attrs['src'], tag))

def main():
    report = json.loads((OUT/'build-report.json').read_text(encoding='utf-8'))
    assert report['legacy_articles'] == 7 and report['project_details'] == 3 and report['notes'] == 2
    docs = {}
    issues = []
    for path in OUT.rglob('*.html'):
        raw = path.read_text(encoding='utf-8')
        if any(marker in raw for marker in ('{{ site.', '__ORIGINAL_LOL_URL__', 'OneDrive', 'CodeX_Workspace')):
            issues.append(f'Unresolved/private content: {path.relative_to(OUT)}')
        doc = Document(); doc.feed(raw); docs[path.resolve()] = doc
        if not path.name.startswith('google') and (not doc.title or not doc.lang):
            issues.append(f'Missing document metadata: {path.name}')
    for path, doc in docs.items():
        route = '/' + path.relative_to(OUT).as_posix()
        for reference, tag in doc.refs:
            parsed = urlsplit(urljoin(route, reference))
            if parsed.scheme or parsed.netloc: continue
            target = OUT / unquote(parsed.path).lstrip('/')
            if parsed.path.endswith('/'): target /= 'index.html'
            if not target.exists():
                issues.append(f'{route}: missing {tag} {reference}'); continue
            if parsed.fragment and target.suffix == '.html':
                target_doc = docs.get(target.resolve())
                if target_doc and unquote(parsed.fragment) not in target_doc.ids:
                    issues.append(f'{route}: missing anchor {reference}')
    for path in report['legacy_routes']:
        assert (OUT/path.lstrip('/')/'index.html').exists(), path
    for name in ['sitemap.xml','feed.xml']: ET.parse(OUT/name)
    about = (OUT/'about/index.html').read_text(encoding='utf-8')
    assert 'New York, NY' not in about and 'technically sophisticated' not in about
    lol = (OUT/'projects/league-of-legends/index.html').read_text(encoding='utf-8')
    assert all(s in lol for s in ['98.81%', '99.13%', '56.17%', '94.05%', '6,369', '本次没有重新训练模型'])
    assert (OUT/'.nojekyll').exists()
    if issues: raise SystemExit('\n'.join(issues))
    print(json.dumps({'status':'passed','html_documents':len(docs),'legacy_routes':7,'project_details':3,'notes':2,'checked':'local links, images, anchors, XML, metadata, source boundaries and legacy route coverage'},ensure_ascii=False))

if __name__ == '__main__': main()
