"""Build the personal website from Markdown and the preserved project archive."""
from __future__ import annotations
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape
import markdown
import yaml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
CONFIG = yaml.safe_load((ROOT / 'content/catalog.yml').read_text(encoding='utf-8'))
PAGES: dict[str, str] = {}
META: dict[str, dict] = {}
E = lambda value: html.escape(str(value), quote=True)

def load(path):
    text = (ROOT / path).read_text(encoding='utf-8-sig')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    return (yaml.safe_load(match[1]) or {}, text[match.end():]) if match else ({}, text)

def render_markdown(text):
    text = text.replace('{{ site.url }}{{ site.baseurl }}', '').replace('{{site.url}}{{site.baseurl}}', '')
    md = markdown.Markdown(extensions=['extra', 'toc', 'sane_lists'], extension_configs={'toc': {'permalink': False}})
    result = md.convert(text)
    result = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy"', result)
    result = result.replace('alt="my photo"', 'alt="原项目图表"')
    result = re.sub(r'<table>', '<div class="table-scroll"><table>', result).replace('</table>', '</table></div>')
    return result, md.toc

def layout(title, body, path, description='', kind='', toc='', article=False, math=False, scripts=()):
    active = 'Projects' if path.startswith('/projects') else 'Notes' if path.startswith('/notes') else 'About' if path == '/about/' else 'Archive' if path.startswith('/archive') else ''
    nav = ''.join(f'<a href="{url}"'+(' aria-current="page"' if label == active else '')+f'>{label}</a>'
                  for label, url in [('Projects','/projects/'),('Notes','/notes/'),('About','/about/')])
    canonical = CONFIG['site_url'] + quote(path, safe='/')
    document_title = title if 'Annan Chen' in title else title + ' · Annan Chen'
    head = f'<title>{E(document_title)}</title><meta name="description" content="{E(description)}"><link rel="canonical" href="{canonical}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{canonical}"><meta property="og:type" content="'+('article' if article else 'website')+'">'
    extra = '<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>' if math else ''
    extra += ''.join(f'<script defer src="{E(src)}"></script>' for src in scripts)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{head}<meta name="theme-color" content="#f7f5f0"><link rel="icon" href="/site-assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/site-assets/style.css">{extra}</head><body>
<a class="skip" href="#content">跳到正文</a><header class="site-header"><a class="wordmark" href="/">Annan Chen<span>陈安楠</span></a><nav aria-label="主导航">{nav}</nav></header>
<main id="content">{body}</main><footer class="site-footer"><span>© 2026 陈安楠</span><div><a href="/archive/">早期项目</a><a href="{E(CONFIG['github'])}">GitHub ↗</a><a href="{E(CONFIG['linkedin'])}">LinkedIn ↗</a></div></footer></body></html>'''

def page(path, title, body, description='', **kwargs):
    assert path.startswith('/') and path.endswith('/') and '..' not in path
    assert path not in PAGES, path
    PAGES[path] = layout(title, body, path, description, **kwargs)
    META[path] = {'title': title, 'description': description}

def heading(kicker, title, intro=''):
    return f'<header class="page-heading"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1>'+ (f'<p class="lead">{E(intro)}</p>' if intro else '')+'</header>'

def project_card(project):
    return f'''<article class="project-card"><a class="project-image" href="{project['path']}"><img src="{project['image']}" alt="{E(project['image_alt'])}" width="1200" height="780" loading="lazy"></a><div class="project-card-body"><p class="meta">{project['year']} <span> / </span> {E(project['category'])}</p><h3><a href="{project['path']}">{E(project['title'])}</a></h3><p>{E(project['summary'])}</p><div class="card-bottom"><span>{E(project['stack'])}</span><a href="{project['path']}" aria-label="阅读{E(project['title'])}">查看项目 ↗</a></div></div></article>'''

def reading_page(path, meta, body, links='', kicker='', image=''):
    rendered, toc = render_markdown(body)
    date = str(meta.get('date', ''))
    if meta.get('updated'): date += ' / 回看 ' + str(meta['updated'])
    head = heading(kicker or meta.get('kind', '项目'), meta['title'])
    info = f'<p class="article-meta">{E(date)}</p>' if date else ''
    buttons = f'<div class="article-links">{links}</div>' if links else ''
    side = f'<aside class="article-toc"><p>目录</p>{toc}</aside>' if '<li>' in toc else ''
    article = f'<div class="article-wrap">{head}{info}{buttons}<div class="reading-layout"><article class="prose">{rendered}</article>{side}</div></div>'
    page(path, meta['title'], article, meta.get('description', ''), article=True, math=meta.get('mathjax', False))

def about_page(meta, body):
    journey = yaml.safe_load((ROOT/'content/journey.yml').read_text(encoding='utf-8'))
    cities = {city['id']: city for city in journey['cities']}
    buttons = ''.join(f'''<button class="city-stop" type="button" data-city="{E(city['id'])}" aria-pressed="false" aria-controls="journey-timeline"><span class="city-point" aria-hidden="true"></span><span class="city-country">{E(city['country'])}</span><strong>{E(city['name'])}</strong><span class="city-english">{E(city['english'])}</span><span class="city-period">{E(city['period'])}</span></button>''' for city in cities.values())
    entries = ''.join(f'''<li class="journey-entry" data-city="{E(chapter['city'])}"><div class="journey-period">{E(chapter['period'])}</div><div class="journey-detail"><p class="journey-meta"><span>{E(cities[chapter['city']]['name'])}</span><span>{E(chapter['kind'])}</span></p><h3>{E(chapter['title'])}</h3><p>{E(chapter['detail'])}</p></div></li>''' for chapter in journey['chapters'])
    roadmap = f'''<section class="journey" aria-labelledby="journey"><div class="journey-heading"><div><p class="eyebrow">2012 — NOW</p><h2 id="journey">城市与经历</h2></div><button type="button" class="journey-reset" data-city="all" aria-pressed="true" aria-controls="journey-timeline">全部地点</button></div><div class="city-route" role="group" aria-label="按城市查看经历">{buttons}</div><p class="sr-only" aria-live="polite" id="journey-status">全部地点，共{len(journey['chapters'])}段经历。</p><ol class="journey-timeline" id="journey-timeline">{entries}</ol></section>'''
    intro, rest = body.split('## 个人项目', 1)
    intro_html, _ = render_markdown(intro)
    rest_html, _ = render_markdown('## 个人项目'+rest)
    content = heading('ABOUT', meta['title'])+f'<div class="prose about-intro">{intro_html}</div>'+roadmap+f'<div class="prose about-more">{rest_html}</div>'
    page('/about/', meta['title'], content, meta.get('description',''), scripts=('/site-assets/journey.js',))

def main():
    legacy = []
    for file in sorted((ROOT / '_posts').glob('[0-9][0-9][0-9][0-9]-*.md'), reverse=True):
        meta, body = load(file.relative_to(ROOT))
        slug = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', file.stem)
        if slug not in CONFIG['legacy']: continue
        view = CONFIG['legacy'][slug]
        route = '/' + '/'.join(str(c).lower() for c in meta.get('categories', [])) + '/' + slug + '/'
        original = {**meta, **view, 'slug': slug, 'original_title': meta['title'], 'path': route, 'body': body}
        legacy.append(original)
    assert len(legacy) == 7, f'Expected seven preserved articles; found {len(legacy)}'
    lol = next(item for item in legacy if item['slug'] == 'LOL-Analysis')
    for item in legacy:
        # Preserve the original English article, with a separate link to any dated revisit.
        intro = f'<div class="archive-note">原文 · {E(item["date"])}'
        if item.get('refresh_path'): intro += f' <a href="{item["refresh_path"]}">阅读 2026 年回看 ↗</a>'
        intro += '</div>'
        body, toc = render_markdown(item['body'])
        content = heading('EARLIER WORK', item['original_title']) + intro
        content += f'<div class="reading-layout"><article class="prose" lang="en">{body}</article><aside class="article-toc"><p>Outline</p>{toc}</aside></div>'
        page(item['path'], item['original_title'], '<div class="article-wrap">'+content+'</div>', item['summary'], article=True, math=item.get('mathjax', False))
    projects = CONFIG['projects']
    cards = ''.join(project_card(p) for p in projects)
    notes = []
    for source in sorted((ROOT/'content/notes').glob('*.md')):
        meta, body = load(source.relative_to(ROOT)); notes.append(meta)
        reading_page(meta['path'], meta, body, kicker='NOTES / 开发笔记')
    def note_rows():
        return ''.join(f'<a class="note-row" href="{n["path"]}"><div><span class="meta">{E(n["kind"])} · {E(n["date"])}</span><h3>{E(n["title"])}</h3><p>{E(n["description"])}</p></div><span aria-hidden="true">↗</span></a>' for n in notes)
    feature = f'''<a class="revisit" href="/projects/league-of-legends/"><div><p class="eyebrow">2020 项目 / 2026 回看</p><h2>英雄联盟：<br>比赛预测与英雄聚类</h2><p>职业赛事数据的胜负预测、英雄聚类与阵容分析。</p><span class="text-link">阅读分析 ↗</span></div><img src="/images/lol/lol11.jpg" alt="英雄联盟原项目插图" loading="lazy"></a>'''
    home = f'''<section class="hero"><div><p class="eyebrow">DATA / GAMES / AI</p><h1>陈安楠<span>Annan Chen</span></h1><p class="hero-intro">{E(CONFIG['intro'])}</p><a class="text-link" href="/about/">关于我 ↗</a></div><div class="hero-portrait"><img src="/site-assets/portrait.jpeg" alt="陈安楠" width="400" height="500"></div></section>
<section class="section"><div class="section-head"><h2>个人项目</h2><a href="/projects/">全部项目 ↗</a></div><div class="project-grid">{cards}</div></section>
<section class="section">{feature}</section><section class="section"><div class="section-head"><h2>开发笔记</h2><a href="/notes/">全部笔记 ↗</a></div>{note_rows()}</section>'''
    page('/', '陈安楠 / Annan Chen', home, CONFIG['intro'])
    listing = ''.join(f'<a class="archive-row" href="{item.get("refresh_path",item["path"])}"><span class="archive-year">{str(item["date"])[:4]}</span><div><h3>{E(item["title"])}</h3><p>{E(item["summary"])}</p></div><span class="archive-type">{E(item["category"])} ↗</span></a>' for item in legacy)
    page('/projects/', '项目', heading('PROJECTS', '项目', 'AI应用、研究工具与数据分析项目。') + f'<div class="project-grid">{cards}</div><section class="section"><div class="section-head"><h2>早期项目</h2><a href="/archive/">按年份查看 ↗</a></div>{listing}</section>', '近期AI工具、科技研究与早期数据分析项目。')
    page('/notes/', '笔记', heading('NOTES', '开发笔记') + note_rows(), 'AI对话记忆和科技研究工具的开发笔记。')
    archive_html = heading('ARCHIVE', '早期项目', '2018—2020年课程与研究项目。')
    for year in ['2020', '2019', '2018']:
        rows = ''.join(f'<a class="archive-row" href="{item["path"]}"><span class="archive-year">{E(item["date"])}</span><div><h3>{E(item["title"])}</h3><p>{E(item["summary"])}</p></div><span aria-hidden="true">↗</span></a>' for item in legacy if str(item['date']).startswith(year))
        archive_html += f'<section class="archive-group" id="{year}"><h2>{year}</h2>{rows}</section>'
    page('/archive/', '早期项目', archive_html, '七个早期项目的原文归档。')
    meta, body = load('content/pages/about.md'); about_page(meta, body)
    for project in projects:
        meta, body = load(project['source'])
        buttons = f'<a class="button" href="{project["demo"]}">打开演示 ↗</a><a class="button secondary" href="{project["repo"]}">GitHub ↗</a>'
        reading_page(project['path'], meta, body, buttons, project['category'])
    meta, body = load('content/projects/league-of-legends.md')
    reading_page(meta['path'], meta, body.replace('__ORIGINAL_LOL_URL__', quote(lol['path'], safe='/')), kicker='项目回看 / LEAGUE OF LEGENDS')
    for alias in ['/category-archive/', '/year-archive/', '/page2/', '/page/2/']:
        PAGES[alias] = f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/archive/"><link rel="canonical" href="{CONFIG["site_url"]}/archive/"><title>项目归档</title></head><body><a href="/archive/">查看项目归档</a></body></html>'
    assert OUT.parent == ROOT and OUT.name == 'dist'
    if (OUT/'build-report.json').exists():
        previous = json.loads((OUT/'build-report.json').read_text(encoding='utf-8'))
        for old_route in set(previous.get('routes', [])) - set(PAGES):
            stale = (OUT/old_route.lstrip('/')/'index.html').resolve()
            assert stale.is_relative_to(OUT.resolve())
            stale.unlink(missing_ok=True)
    OUT.mkdir(exist_ok=True)
    for route, content in PAGES.items():
        target = OUT/route.lstrip('/')/'index.html'; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(content, encoding='utf-8')
    shutil.copytree(ROOT/'site_assets', OUT/'site-assets', dirs_exist_ok=True)
    shutil.copytree(ROOT/'images', OUT/'images', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.DS_Store','Thumbs.db'))
    for verification in ROOT.glob('google*.html'): shutil.copyfile(verification, OUT/verification.name)
    (OUT/'.nojekyll').write_text('', encoding='utf-8')
    (OUT/'404.html').write_text(layout('找不到这个页面', heading('404', '这个地址没有页面')+'<p><a class="text-link" href="/">回到首页 ↗</a></p>', '/404/', '页面不存在。'), encoding='utf-8')
    urls = ''.join('<url><loc>'+xml_escape(CONFIG['site_url']+quote(path,safe='/'))+'</loc></url>' for path in META)
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>', encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+CONFIG['site_url']+'/sitemap.xml\n', encoding='utf-8')
    items = ''.join('<item><title>'+xml_escape(n['title'])+'</title><link>'+CONFIG['site_url']+n['path']+'</link><guid>'+CONFIG['site_url']+n['path']+'</guid><description>'+xml_escape(n['description'])+'</description></item>' for n in notes)
    (OUT/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Annan Chen</title><link>'+CONFIG['site_url']+'</link><description>Projects and notes</description>'+items+'</channel></rss>', encoding='utf-8')
    report = {'pages': len(PAGES), 'legacy_articles': len(legacy), 'project_details': 3, 'notes': len(notes), 'legacy_routes': [i['path'] for i in legacy], 'routes': list(PAGES)}
    (OUT/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__': main()
