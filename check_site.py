"""Check generated routes, assets, anchors and publication boundaries."""
from html.parser import HTMLParser
import json
import re
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
    assert report['languages'] == ['zh','en'] and len(report['full_translations']) == 7
    assert len(report['routes']) == 44
    docs = {}
    issues = []
    for path in OUT.rglob('*.html'):
        raw = path.read_text(encoding='utf-8')
        if any(marker in raw for marker in ('{{ site.', '__ORIGINAL_LOL_URL__', 'OneDrive')) or re.search(r'[A-Z]:[/\\]Users[/\\]',raw):
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
        zh = (OUT/path.lstrip('/')/'index.html').read_text(encoding='utf-8')
        en = (OUT/'en'/path.lstrip('/')/'index.html').read_text(encoding='utf-8')
        assert '中文全文' in zh and 'English original · 完整英文原文' in zh
        assert 'READING GUIDE' in en and 'Full original article' in en
    for route in report['paired_routes']:
        raw = (OUT/route.lstrip('/')/'index.html').read_text(encoding='utf-8')
        assert 'hreflang="zh-CN"' in raw and 'hreflang="en"' in raw
        assert 'data-set-lang="zh"' in raw and 'data-set-lang="en"' in raw
        assert ('<html lang="en"' in raw) == route.startswith('/en/')
        assert 'fonts.googleapis.com' not in raw
    for lang in ('','en/'):
        about = (OUT/lang/'about/index.html').read_text(encoding='utf-8')
        assert about.count('class="journey-record"') == 7
        assert about.count('<summary>') == 7 and 'class="awards"' not in about
        assert '/site-assets/organizations/netease.' in about
        assert 'EXL / Amex' in about and '2012—2015' in about and '2018.04—08' in about
        assert 'CFA' not in about and 'HSBC' not in about
        projects = (OUT/lang/'projects/index.html').read_text(encoding='utf-8')
        assert projects.count('data-project ') == 9 and 'id="project-search"' in projects
    import importlib.util
    spec=importlib.util.spec_from_file_location('site_builder',ROOT/'build.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    for source in (ROOT/'_posts').glob('[0-9]*.md'):
        slug=builder.re.sub(r'^\d{4}-\d{2}-\d{2}-','',source.stem)
        if slug not in builder.CONFIG['legacy']:continue
        meta,body=builder.load(source.relative_to(ROOT))
        rendered,_=builder.render_markdown(body,'en','orig-')
        route='/'+'/'.join(str(c).lower() for c in meta.get('categories',[]))+'/'+slug+'/'
        for prefix in ('','en/'):
            raw=(OUT/prefix/route.lstrip('/')/'index.html').read_text(encoding='utf-8')
            assert rendered in raw, 'Original article changed: '+slug
        translated=(ROOT/'content/translations/zh'/(slug+'.md')).read_text(encoding='utf-8')
        normalized=lambda text: text.replace('{{ site.url }}{{ site.baseurl }}','').replace('{{site.url}}{{site.baseurl}}','')
        refs=lambda text: builder.re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',normalized(text))
        assert refs(body) == refs(translated), 'Translation links/figures: '+slug
    assert (OUT/'site-assets/site.js').exists()
    enabled=json.loads((ROOT/'content/analytics.json').read_text(encoding='utf-8'))['enabled']
    home=(OUT/'index.html').read_text(encoding='utf-8')
    assert ('src="/site-assets/analytics.js"' in home) == enabled
    if enabled:assert (OUT/'site-assets/analytics.js').exists()
    for name in ['sitemap.xml','feed.xml']: ET.parse(OUT/name)
    about = (OUT/'about/index.html').read_text(encoding='utf-8')
    assert 'New York, NY' not in about and 'technically sophisticated' not in about
    lol = (OUT/'projects/league-of-legends/index.html').read_text(encoding='utf-8')
    assert all(s in lol for s in ['98.81%', '99.13%', '56.17%', '94.05%', '6369', '本次没有重新训练模型'])
    assert (OUT/'.nojekyll').exists()
    if issues: raise SystemExit('\n'.join(issues))
    print(json.dumps({'status':'passed','html_documents':len(docs),'legacy_routes':7,'project_details':3,'notes':2,'checked':'local links, images, anchors, XML, metadata, source boundaries and legacy route coverage'},ensure_ascii=False))

if __name__ == '__main__': main()
