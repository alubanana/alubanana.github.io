"""Build paired Chinese/English pages from editable Markdown sources."""
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
PAGES, META = {}, {}
E = lambda x: html.escape(str(x), quote=True)
SITE = CONFIG['site_url']
ANALYTICS = 'https://annan-site-analytics.regalpig32.chatgpt.site'
TRACKING_ENABLED = json.loads((ROOT/'content/analytics.json').read_text(encoding='utf-8'))['enabled']

def tr(zh, en, lang): return en if lang == 'en' else zh
def url(path, lang): return '/en' + path if lang == 'en' else path

def load(path):
    text = (ROOT / path).read_text(encoding='utf-8-sig')
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    return (yaml.safe_load(match[1]) or {}, text[match.end():]) if match else ({}, text)

def render_markdown(text, lang='zh', prefix=''):
    text = text.replace('{{ site.url }}{{ site.baseurl }}', '').replace('{{site.url}}{{site.baseurl}}', '')
    md = markdown.Markdown(extensions=['extra', 'toc', 'sane_lists'])
    result = md.convert(text)
    result = re.sub(r'<img\b(?![^>]*\bloading=)', '<img loading="lazy"', result)
    result = result.replace('alt="my photo"', 'alt="'+tr('原项目图表','Original project figure',lang)+'"')
    result = result.replace('<table>', '<div class="table-scroll"><table>').replace('</table>', '</table></div>')
    if lang == 'en':
        result = re.sub(r'href="(/(?:projects|notes|about|archive|privacy)/[^\"]*)"', lambda m: 'href="/en'+m[1]+'"', result)
    toc = md.toc
    if prefix:
        result = re.sub(r'id="([^"]+)"', lambda m:'id="'+prefix+m[1]+'"',result)
        result = re.sub(r'href="#([^"]+)"', lambda m:'href="#'+prefix+m[1]+'"',result)
        toc = re.sub(r'href="#([^"]+)"', lambda m:'href="#'+prefix+m[1]+'"',toc)
    return result, toc

def icon(kind):
    paths = {'school':'M3 9l9-6 9 6-9 5z M6 11v7q6 4 12 0v-7 M21 9v8',
             'work':'M8 7V4h8v3 M3 7h18v14H3z M3 12q9 5 18 0 M12 12v4',
             'pin':'M18 10c0 5-6 11-6 11S6 15 6 10a6 6 0 1 1 12 0z M10 10a2 2 0 1 0 4 0a2 2 0 1 0-4 0',
             'award':'M8 3h8v8q-4 5-8 0z M8 5H4v3q0 5 4 4 M16 5h4v3q0 5-4 4 M12 14v6 M8 21h8',
             'arrow':'M4 12h16 M13 5l7 7-7 7'}
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="'+paths[kind]+'"/></svg>'

def artwork(key):
    """Small deterministic drawings, each linked to a real project."""
    seed = sum(map(ord,key))
    colors = ['#d9e8d3','#f3d6ba','#d5ddf4','#e8d3e2','#f3e69c']
    bg = colors[seed % len(colors)]
    if key in ('tech-research','ai-memory'):
        coords = [(45,130),(130,57),(218,147),(315,68),(390,142)]
        shapes = ''.join(f'<path d="M{x},{y}L{coords[(i+1)%5][0]},{coords[(i+1)%5][1]}"/>' for i,(x,y) in enumerate(coords))
        shapes += ''.join(f'<circle cx="{x}" cy="{y}" r="{10+i*2}" fill="{bg}"/><circle cx="{x}" cy="{y}" r="3" fill="currentColor"/>' for i,(x,y) in enumerate(coords))
        if key == 'ai-memory': shapes += '<rect x="178" y="58" width="74" height="44" rx="4" fill="'+bg+'"/><path d="M193 72h40 M193 82h25"/>'
    elif 'NBA' in key:
        shapes = '<path d="M30 30h380v150H30z M220 30v150 M30 64h82v82H30 M410 64h-82v82h82 M30 54a65 65 0 0 1 0 104 M410 54a65 65 0 0 0 0 104"/><circle cx="220" cy="105" r="28"/>'
        shapes += ''.join(f'<circle cx="{45+(i*43)%355}" cy="{45+(i*29)%125}" r="3" fill="currentColor" stroke="none"/>' for i in range(22))
    elif key == 'LOL-Analysis':
        shapes = ''.join(f'<circle cx="{55+i*34}" cy="{45+((i*37)%110)}" r="{6+i%4*3}" fill="currentColor" opacity=".{4+i%5}"/>' for i in range(10))
        shapes += '<path stroke-dasharray="4 6" d="M15 170Q130-15 230 115T430 80"/>'
    elif key == 'Hey-Tea-Operation-Simulation':
        shapes = ''.join(f'<rect x="{35+i*44}" y="{40+i%2*40}" width="26" height="26" rx="13"/>' for i in range(6))
        shapes += '<path d="M40 150h230l45-45h100 M315 105l-25-25 M315 105l-25 25"/><rect x="345" y="65" width="45" height="75" rx="9"/>'
    elif key == 'Tools-Squirrel':
        shapes = '<path d="M25 40l390 115 M40 175L385 25 M160 15l-35 180 M275 15l-35 180" opacity=".3"/>'
        shapes += ''.join(f'<circle cx="{80+i*85}" cy="{70+i%2*60}" r="12" fill="'+bg+'"/>' for i in range(4))
    else:
        shapes = '<path d="M25 170h390 M45 25v160" opacity=".4"/>'
        shapes += ''.join(f'<path d="M45 {130+i*13}Q120 {20+i*17} 205 {115-i*12}T405 {35+i*15}" opacity=".{4+i}"/>' for i in range(4))
    return f'<svg viewBox="0 0 440 210" aria-hidden="true" class="cover-art" style="background:{bg}"><g fill="none" stroke="#173b33" stroke-width="2">{shapes}</g><text x="22" y="195" fill="#173b33" font-family="monospace" font-size="10">{E(key.upper().replace("-"," / "))}</text></svg>'

def heading(kicker,title,intro=''):
    return f'<header class="page-heading"><p class="eyebrow">{E(kicker)}</p><h1>{E(title)}</h1>'+ (f'<p class="lead">{E(intro)}</p>' if intro else '')+'</header>'

def layout(title, body, path, lang, description='', article=False, math=False):
    current = url(path,lang)
    doc_title = title if "Annan Chen" in title else title + " · Annan Chen"
    en = SITE + quote(url(path,'en'),safe='/')
    zh = SITE + quote(path,safe='/')
    nav = ''.join(f'<a href="{url(p,lang)}"'+(' aria-current="page"' if path.startswith(p) else '')+f'>{tr(z,e,lang)}</a>' for z,e,p in [('项目','Projects','/projects/'),('笔记','Notes','/notes/'),('关于','About','/about/')])
    langs = ''.join(f'<a href="{url(path,l)}" data-set-lang="{l}" lang="'+('en' if l=='en' else 'zh-CN')+'"'+(' aria-current="true"' if l==lang else '')+'>'+label+'</a>' for l,label in [('zh','中文'),('en','EN')])
    extra = '<script>window.MathJax={tex:{inlineMath:[["$","$"],["\\\\(","\\\\)"]]}};</script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>' if math else ''
    tracking_control = '<button id="analytics-toggle" type="button" lang="en">Analytics settings</button>' if TRACKING_ENABLED else ''
    tracking_script = f'<script defer src="/site-assets/analytics.js" data-endpoint="{ANALYTICS}/api/collect"></script>' if TRACKING_ENABLED else ''
    return f'''<!doctype html><html lang="{'en' if lang=='en' else 'zh-CN'}" data-locale="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(doc_title)}</title><meta name="description" content="{E(description)}"><link rel="canonical" href="{SITE+quote(current,safe='/')}"><link rel="alternate" hreflang="zh-CN" href="{zh}"><link rel="alternate" hreflang="en" href="{en}"><link rel="alternate" hreflang="x-default" href="{zh}"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(description)}"><meta property="og:url" content="{SITE+quote(current,safe='/')}"><meta name="theme-color" content="#f5f4ed"><link rel="icon" href="/site-assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/site-assets/studio.css">{extra}<script defer src="/site-assets/site.js"></script>{tracking_script}</head><body data-content-id="{E(path)}" data-article="{str(article).lower()}"><a class="skip" href="#content">{tr('跳到正文','Skip to content',lang)}</a><header class="site-header"><a class="wordmark" href="{url('/',lang)}">ac<span>Annan Chen<br><small>陈安楠</small></span></a><nav aria-label="{tr('主导航','Main navigation',lang)}">{nav}</nav><div class="language-switch" aria-label="Language / 语言">{langs}</div></header><main id="content">{body}</main><footer class="site-footer"><span>© 2026 Annan Chen</span><div><a href="{url('/archive/',lang)}">{tr('早期项目','Archive',lang)}</a><a href="{E(CONFIG['github'])}">GitHub ↗</a><a href="{E(CONFIG['linkedin'])}">LinkedIn ↗</a><a href="{url('/privacy/',lang)}">{tr('访问统计','Analytics',lang)}</a>{tracking_control}</div></footer></body></html>'''

def page(path,title,body,lang,description='',**kw):
    route=url(path,lang)
    assert route not in PAGES and route.startswith('/') and route.endswith('/')
    PAGES[route]=layout(title,body,path,lang,description,**kw)
    META[route]={'title':title,'description':description,'lang':lang,'base':path}

def reading_page(path,meta,body,lang,links='',kicker=''):
    rendered,toc=render_markdown(body,lang)
    side = f'<aside class="article-toc"><p>{tr("目录","Contents",lang)}</p>{toc}</aside>' if '<li>' in toc else ''
    dates=str(meta.get('date',''))
    if meta.get('updated'):dates+=' · '+tr('回看 ','Revisited ',lang)+str(meta['updated'])
    content=heading(kicker or tr('文章','ARTICLE',lang),meta['title'])+f'<p class="article-meta">{E(dates)}</p>'
    if links:content+='<div class="article-links">'+links+'</div>'
    page(path,meta['title'],'<div class="article-wrap">'+content+f'<div class="reading-layout"><article class="prose">{rendered}</article>{side}</div></div>',lang,meta.get('description',''),article=True,math=meta.get('mathjax',False))

EN_PROJECTS={
'tech-research':('Technology research radar','Technical progress, papers and companies, with a history of research judgments.','Research tool'),
'ai-memory':('AI conversation memory','Incremental imports, source versions and current topic state for long-running AI work.','AI tool'),
'LOL-Analysis':('League of Legends: prediction & clusters','Compare match prediction models and champion groups using professional match data.','Game analytics'),
'Hey-Tea-Operation-Simulation':('HEYTEA: ordering the queue','Discrete-event simulation of online and in-store order priorities.','Simulation'),
'LSTM-Prediction-on-Private-Equity':('Private equity cash flow forecasting','Sequence models and macroeconomic features for fund contribution forecasts.','Time series'),
'NBA-Database-Design':('NBA database & query app','A PostgreSQL database and Flask application for NBA records.','Web / Data'),
'Election-Prediction':('U.S. election forecasting','A historical prediction study combining demographics and social media.','Prediction'),
'Tools-Squirrel':('Central Park squirrel sightings','A Django application for managing sightings, maps and summary statistics.','Web app'),
'NBA-Shot-Prediction':('NBA shot prediction','Classification models and feature selection for shot outcomes.','Sports analytics')}

def card(p,lang):
    title,summary,category=EN_PROJECTS[p['id']] if lang=='en' else (p['title'],p['summary'],p['category'])
    return f'<article class="project-card" data-project data-category="{p["filter"]}" data-search="{E(title+" "+summary+" "+category+" "+p["id"]+" "+EN_PROJECTS[p["id"]][0])}"><a class="project-image" href="{url(p["path"],lang)}" aria-label="{E(title)}">{artwork(p["id"])}</a><div class="project-card-body"><p class="meta">{E(p["year"])} <span>/</span> {E(category)}</p><h3><a href="{url(p["path"],lang)}">{E(title)}</a></h3><p>{E(summary)}</p><a class="card-link" href="{url(p["path"],lang)}">{tr("查看项目","Read project",lang)} {icon("arrow")}</a></div></article>'

JOURNEY=yaml.safe_load((ROOT/"content/timeline.yml").read_text(encoding="utf-8"))["timeline"]
ORGANIZATIONS={
    'fuzhou':('福州一中','fuzhou.jpg'),
    'cuhksz':('CUHK-Shenzhen','cuhksz.png'),
    'tencent':('Tencent','tencent.png'),
    'coca-cola':('Coca-Cola','coca-cola.png'),
    'columbia':('Columbia University','columbia.png'),
    'exl':('EXL','exl.png'),
    'amex':('American Express','amex.svg'),
    'netease':('NetEase Games','netease.png')}

def timeline(lang):
    rows=''
    for entry in JOURNEY:
        marks=''.join(f'<img src="/site-assets/organizations/{ORGANIZATIONS[key][1]}" alt="{E(ORGANIZATIONS[key][0])}" width="48" height="48" loading="lazy">' for key in entry['logos'])
        links=''.join(f'<a href="{url(item["path"],lang)}">{E(item["label"][lang])} <span aria-hidden="true">↗</span></a>' for item in entry.get('links',[]))
        photos=''.join(f'<figure><img src="{E(photo["src"])}" alt="{E(photo["alt"][lang])}" loading="lazy"><figcaption>{E(photo.get("caption",{}).get(lang,""))}</figcaption></figure>' for photo in entry.get('photos',[]))
        rows+=f'''<li id="{E(entry['id'])}"><div class="journey-period">{E(entry['period'])}</div><div data-org="{E(entry['id'])}" class="timeline-mark{' paired' if len(entry['logos'])>1 else ''}">{marks}</div><details class="journey-record"><summary><span class="journey-summary"><span class="journey-title">{E(entry['title'][lang])}</span><span class="journey-subtitle">{E(entry['detail'][lang])}</span></span><span class="record-indicator" aria-hidden="true">+</span></summary><div class="journey-entry"><p>{E(entry['record'][lang])}</p>{photos}{'<div class="journey-links">'+links+'</div>' if links else ''}</div></details></li>'''
    return '<section class="journey" aria-labelledby="journey">'+f'<div class="section-head"><h2 id="journey">{tr("经历","Journey",lang)}</h2><span class="meta">2012 → NOW</span></div><ol class="journey-timeline">'+rows+'</ol></section>'

GUIDES={
'LOL-Analysis':(['赛事数据','英雄表示','两类预测任务','独立评估'],['Match data','Champion features','Two prediction tasks','Evaluation'],'对局指标模型包含赛后信息，测试准确率约97%—99%；只使用阵容分组计数时约52%—56%。阅读时要先区分这两个任务。结题报告采用20个常规聚类和1个补充分组，形成42维阵容输入；2026年回看另列评估改进。','The match-statistics task includes post-match information and reaches roughly 97–99% test accuracy; composition group counts reach about 52–56%. These are different tasks. The final report uses 20 regular clusters plus a fallback group, giving 42 composition features. The dated revisit discusses evaluation improvements.'),
'Hey-Tea-Operation-Simulation':(['线上 / 门店到达','订单队列','服务优先级 θ','收入 / 等待时间'],['Online / store arrivals','Order queues','Priority parameter θ','Revenue / waiting time'],'项目用离散事件模拟比较两类订单的服务顺序。收入、等待时间和惩罚后收入对应不同目标，不能共用一个“最优”结论。原文惩罚后收入小节写θ=0.1，政策建议写θ=0.8；结果部分还混入一段LSTM文字，均保留供复核。','A discrete-event model compares priorities for online and in-store orders. Revenue, waiting time and penalized revenue are different objectives. The original reports θ=0.1 in the penalized-revenue section but recommends θ=0.8 later. An unrelated LSTM paragraph also appears in its results; both are retained in the archive.'),
'LSTM-Prediction-on-Private-Equity':(['季度现金流','插值与扰动','LSTM系列模型','训练 / 测试比较'],['Quarterly cash flow','Interpolation + noise','LSTM model variants','Train / test comparison'],'项目比较LSTM、Encoder–Decoder、CNN–LSTM和ConvLSTM等结构。原始季度基准经过插值及高斯噪声处理，得到更密的序列；这些点没有增加真实独立观测。阅读结果时，需要把数据构造、模型比较与真实基金现金流的验证分开。','The project compares LSTM, encoder–decoder, CNN–LSTM and ConvLSTM variants. Quarterly benchmark data is interpolated and perturbed with Gaussian noise. The denser sequence does not add independent real observations; data construction and model comparisons need to be distinguished from validation on actual fund cash flows.'),
'NBA-Database-Design':(['NBA资料','关系数据库','SQL查询','Flask界面'],['NBA records','Relational database','SQL queries','Flask interface'],'从球员、球队、教练与球馆的关系设计，到SQL查询和Web界面，是本项目的主要链路。页面中的赛程、新闻和云端演示均属于当年版本。历史数据库口令已隐去，查询代码和正文继续保留。','The project connects a relational design for players, teams, coaches and stadiums to SQL queries and a Flask interface. Schedules, news and the cloud demo belong to the historical version. A legacy database password has been removed; queries and article text remain available.'),
'Election-Prediction':(['人口 / 历史选票','地区模型','州级汇总','历史结果检验'],['Demographics / past votes','District model','State aggregation','Outcome check'],'这份2019年研究预测特朗普赢得2020年大选，结果未实现。美国国家档案馆记录的实际选举人票为拜登306票、特朗普232票。原文完整保留，适合回看地区建模、时间外验证，以及把社交媒体热度当作选票信号的局限。','This 2019 project predicted a Trump victory in 2020, which did not occur. The National Archives records 306 electoral votes for Biden and 232 for Trump. The complete original remains useful for examining district modeling, out-of-time validation and the limits of treating social-media attention as voting evidence.'),
'Tools-Squirrel':(['2018观察记录','CSV导入','Django增删改查','地图与统计'],['2018 sighting records','CSV import','Django CRUD','Map + statistics'],'应用围绕中央公园松鼠观察数据，提供导入导出、记录维护、地图和统计。原文开头的虚构人物故事属于课程情境；项目贡献应从数据和Web功能来阅读。','The application imports and exports Central Park squirrel observations, maintains sightings, and presents maps and summary statistics. The fictional character in the opening is part of the assignment scenario; the project itself concerns the data and web application.'),
'NBA-Shot-Prediction':(['投篮情境数据','特征筛选','分类模型','验证与解释'],['Shot context','Feature selection','Classification models','Validation + interpretation'],'项目围绕投篮位置、时间等情境特征比较分类器和特征选择。特征重要性受数据字段与模型影响，不能直接推导球员技能不重要。原文RFE示例的语法和部分指标命名不完整，译文保留这些历史表述，后续复现实验时需核对。','The project compares classifiers and feature selection using shot location, time and related context. Feature importance depends on the available variables and model, and does not establish that player skill is unimportant. The original RFE example and some metric labels are incomplete; the translation preserves those historical details.')}

def overview(slug,lang):
    zh,en,ztext,etext=GUIDES[slug]
    labels=en if lang=='en' else zh
    nodes=''.join(f'<div><span>0{i+1}</span><strong>{E(label)}</strong></div>' for i,label in enumerate(labels))
    source = '<a href="https://www.archives.gov/electoral-college/2020">'+tr('2020年实际结果','2020 official outcome',lang)+' ↗</a>' if slug=='Election-Prediction' else ''
    return f'<section class="reading-guide" aria-labelledby="guide"><p class="eyebrow">2026.11.01 / {tr("阅读导引","READING GUIDE",lang)}</p><h2 id="guide">{tr("项目概览","Project overview",lang)}</h2><div class="flow-diagram">{nodes}</div><p>{E(tr(ztext,etext,lang))}</p>{source}</section>'

def main():
    legacy=[]
    for f in sorted((ROOT/'_posts').glob('[0-9][0-9][0-9][0-9]-*.md'),reverse=True):
        meta,body=load(f.relative_to(ROOT));slug=re.sub(r'^\d{4}-\d{2}-\d{2}-','',f.stem)
        if slug not in CONFIG['legacy']:continue
        view=CONFIG['legacy'][slug]
        route='/'+'/'.join(str(c).lower() for c in meta.get('categories',[]))+'/'+slug+'/'
        legacy.append({**meta,**view,'id':slug,'path':route,'body':body,'original_title':meta['title'],'year':str(meta['date'])[:4],'filter':'web' if slug in ('NBA-Database-Design','Tools-Squirrel') else 'data'})
    assert len(legacy)==7
    lol=next(x for x in legacy if x['id']=='LOL-Analysis')
    recent=[{**p,'filter':'ai'} for p in CONFIG['projects']]
    all_projects=recent+legacy
    translations=[]
    for lang in ('zh','en'):
        for item in legacy:
            slug=item['id'];original,toc=render_markdown(item['body'],'en','orig-')
            title=item['title'] if lang=='zh' else EN_PROJECTS[slug][0]
            content=heading(tr('早期项目','EARLIER WORK',lang),title)+f'<p class="article-meta">{item["date"]} · {E(item["original_title"])}</p>'+overview(slug,lang)
            if item.get('refresh_path'):content+=f'<a class="button secondary" href="{url(item["refresh_path"],lang)}">{tr("2026年回看","2026 revisit",lang)} ↗</a>'
            if lang=='zh':
                source=ROOT/'content/translations/zh'/(slug+'.md')
                assert source.is_file(),f'Missing full translation: {slug}'
                translated,ztoc=render_markdown(source.read_text(encoding='utf-8'),'zh','zh-')
                translations.append(slug)
                content+='<div class="article-edition"><span>中文全文</span><a href="#original-en">English original ↓</a></div>'
                content+=f'<div class="reading-layout"><article class="prose" lang="zh-CN">{translated}</article><aside class="article-toc"><p>目录</p>{ztoc}</aside></div>'
                content+=f'<details class="original-article" id="original-en"><summary>English original · 完整英文原文</summary><article class="prose" lang="en">{original}</article></details>'
            else:
                content+='<div class="article-edition"><span>Full original article</span><a href="'+item['path']+'" data-set-lang="zh">中文全文 ↗</a></div>'
                content+=f'<div class="reading-layout"><article class="prose" id="original-en" lang="en">{original}</article><aside class="article-toc"><p>Contents</p>{toc}</aside></div>'
            page(item['path'],title,'<div class="article-wrap">'+content+'</div>',lang,tr(item['summary'],EN_PROJECTS[slug][1],lang),article=True,math=item.get('mathjax',False))
        notes=[]
        for f in sorted((ROOT/'content/notes').glob('*.md')):
            meta,body=load(f.relative_to(ROOT))
            if lang=='en':em,body=load('content/en/'+f.name);meta={**meta,**em}
            notes.append(meta);reading_page(meta['path'],meta,body,lang,kicker=tr('开发笔记','NOTES',lang))
        def note_rows():
            return ''.join(f'<a class="note-row" href="{url(n["path"],lang)}"><div><span class="meta">{E(n["date"])}</span><h3>{E(n["title"])}</h3><p>{E(n["description"])}</p></div>{icon("arrow")}</a>' for n in notes)
        intro=tr(CONFIG['intro'],'I work in game analytics and build AI applications. This is a collection of projects, development notes and earlier data science work.',lang)
        featured=[recent[0],recent[1],{**lol,'path':'/projects/league-of-legends/'}]
        hero=f'<section class="hero"><div><p class="eyebrow">DATA / GAMES / AI</p><h1>{tr("陈安楠","Annan Chen",lang)}<span>{tr("Annan Chen","陈安楠",lang)}</span></h1><p class="hero-intro">{E(intro)}</p><div class="hero-actions"><a class="button" href="{url("/projects/",lang)}">{tr("浏览项目","Explore projects",lang)} {icon("arrow")}</a><a class="text-link" href="{url("/about/",lang)}">{tr("关于我","About me",lang)} ↗</a></div></div><a class="hero-lab" href="{url("/projects/tech-research/",lang)}" aria-label="{tr("科技周期研究","Technology research radar",lang)}"><div class="lab-orbit"><span class="orbit orbit-one"></span><span class="orbit orbit-two"></span><span class="orbit orbit-three"></span><strong>2036</strong><span class="lab-node n1">AI</span><span class="lab-node n2">ENERGY</span><span class="lab-node n3">BIO</span><span class="lab-node n4">ROBOTICS</span></div><div class="lab-caption"><span>{tr("科技周期研究","TECHNOLOGY RADAR",lang)}</span>{icon("arrow")}</div></a></section>'
        radar=f'<section class="radar-feature"><div><p class="eyebrow">LIVE DEMO / 2026.11.01</p><h2>{tr("科技周期研究","Technology research radar",lang)}</h2><p>{tr("从技术进展、公司与论文，查看不同方向的证据与判断。","Explore evidence and judgments across technical progress, companies and papers.",lang)}</p><div class="radar-counts"><span><b>5</b>{tr("主线","themes",lang)}</span><span><b>10</b>{tr("方向","directions",lang)}</span><span><b>18</b>{tr("公司","companies",lang)}</span></div><a class="button light" data-event="demo_open" href="{recent[0]["demo"]}">{tr("打开研究雷达","Open the radar",lang)} ↗</a></div><a class="radar-art" href="{recent[0]["demo"]}" data-event="demo_open" aria-label="{tr("打开科技研究演示","Open technology research demo",lang)}">{artwork("tech-research")}</a></section>'
        home=hero+f'<section class="section"><div class="section-head"><h2>{tr("项目选集","Selected projects",lang)}</h2><a href="{url("/projects/",lang)}">{tr("全部项目","All projects",lang)} ↗</a></div><div class="project-grid">'+''.join(card(p,lang) for p in featured)+'</div></section>'+radar+f'<section class="section"><div class="section-head"><h2>{tr("笔记","Notes",lang)}</h2></div>{note_rows()}</section>'
        page('/',tr('陈安楠 · 项目与笔记','Annan Chen · Projects & notes',lang),home,lang,intro)
        filters=''.join(f'<button type="button" data-filter="{value}" aria-pressed="{str(value=="all").lower()}">{label}</button>' for value,label in [('all',tr('全部','All',lang)),('ai','AI'),('data',tr('数据分析','Data',lang)),('web','Web')])
        library=heading('PROJECTS',tr('项目库','Project library',lang))+f'<div class="library-controls"><div class="project-filters" role="group" aria-label="{tr("项目类别","Project categories",lang)}">{filters}</div><label class="search-field"><span class="sr-only">{tr("搜索项目","Search projects",lang)}</span><input id="project-search" type="search" placeholder="{tr("搜索项目…","Search projects…",lang)}"></label></div><p class="result-count" id="project-count" aria-live="polite">9 {tr("个项目","projects",lang)}</p><div class="project-grid library-grid">'+''.join(card(p,lang) for p in all_projects)+'</div>'+f'<p id="project-empty" hidden>{tr("没有匹配的项目。","No matching projects.",lang)}</p>'+radar
        page('/projects/',tr('项目库','Project library',lang),library,lang,tr('AI应用、科技研究与数据分析项目。','AI applications, technology research and data science projects.',lang))
        page('/notes/',tr('笔记','Notes',lang),heading('NOTES',tr('开发笔记','Development notes',lang))+note_rows(),lang,tr('AI记忆和科技研究的开发记录。','Development notes on AI memory and technology research.',lang))
        archive=heading('ARCHIVE',tr('早期项目','Earlier projects',lang),tr('2018—2020年的课程与研究项目。','Course and research projects from 2018–2020.',lang))
        for year in ('2020','2019','2018'):
            archive+=f'<section class="archive-group"><h2>{year}</h2>' + ''.join(f'<a class="archive-row" href="{url(i["path"],lang)}"><span class="meta">{i["date"]}</span><div><h3>{E(tr(i["title"],EN_PROJECTS[i["id"]][0],lang))}</h3><p>{E(tr(i["summary"],EN_PROJECTS[i["id"]][1],lang))}</p></div>{icon("arrow")}</a>' for i in legacy if i['year']==year)+'</section>'
        page('/archive/',tr('早期项目','Earlier projects',lang),archive,lang)
        for p in recent:
            meta,body=load(p['source'])
            if lang=='en':em,body=load('content/en/'+p['id']+'.md');meta={**meta,**em}
            links=f'<a class="button" href="{p["demo"]}" data-event="demo_open">{tr("打开演示","Open demo",lang)} ↗</a><a class="button secondary" href="{p["repo"]}">GitHub ↗</a>'
            reading_page(p['path'],meta,body,lang,links,kicker=tr(p['category'],EN_PROJECTS[p['id']][2],lang))
        meta,body=load('content/projects/league-of-legends.md')
        if lang=='en':em,body=load('content/en/league-of-legends.md');meta={**meta,**em}
        reading_page('/projects/league-of-legends/',meta,body.replace('__ORIGINAL_LOL_URL__',quote(url(lol['path'],lang),safe='/')),lang,kicker=tr('项目回看','PROJECT REVISIT',lang))
        meta,body=load('content/'+('en' if lang=='en' else 'pages')+'/about.md')
        intro,rest=body.split('## Personal projects' if lang=='en' else '## 个人项目',1)
        before,_=render_markdown(intro,lang);after,_=render_markdown(('## Personal projects' if lang=='en' else '## 个人项目')+rest,lang)
        page('/about/',meta['title'],heading('ABOUT',meta['title'])+f'<div class="prose about-intro">{before}</div>'+timeline(lang)+f'<div class="prose about-more">{after}</div>',lang,meta.get('description',''))
        meta,body=load('content/'+('en' if lang=='en' else 'pages')+'/privacy.md')
        if not TRACKING_ENABLED: body=tr('访问统计尚未启用。以下为拟采用的记录范围与设置。\n\n','Analytics is not enabled. The planned scope and controls are described below.\n\n',lang)+body
        reading_page('/privacy/',meta,body,lang,kicker='ANALYTICS')
        for alias in ('/category-archive/','/year-archive/','/page2/','/page/2/'):
            target=url('/archive/',lang);PAGES[url(alias,lang)]=f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}"><title>Archive</title></head><body><a href="{target}">Archive</a></body></html>'
    OUT.mkdir(exist_ok=True)
    if (OUT/'build-report.json').exists():
        for old in set(json.loads((OUT/'build-report.json').read_text(encoding='utf-8')).get('routes',[]))-set(PAGES):
            target=(OUT/old.lstrip('/')/'index.html').resolve();assert target.is_relative_to(OUT.resolve());target.unlink(missing_ok=True)
    for route,content in PAGES.items():
        target=OUT/route.lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content,encoding='utf-8')
    shutil.copytree(ROOT/'site_assets',OUT/'site-assets',dirs_exist_ok=True)
    shutil.copytree(ROOT/'images',OUT/'images',dirs_exist_ok=True,ignore=shutil.ignore_patterns('.DS_Store','Thumbs.db'))
    for f in ROOT.glob('google*.html'):shutil.copyfile(f,OUT/f.name)
    (OUT/'.nojekyll').write_text('',encoding='utf-8')
    (OUT/'404.html').write_text(layout('404',heading('404','Page not found')+'<a href="/">Home / 首页</a>','/','zh'),encoding='utf-8')
    urls=''.join('<url><loc>'+xml_escape(SITE+quote(p,safe='/'))+'</loc></url>' for p in META)
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>',encoding='utf-8')
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+SITE+'/sitemap.xml\n',encoding='utf-8')
    items=''.join('<item><title>'+xml_escape(n['title'])+'</title><link>'+SITE+n['path']+'</link><guid>'+SITE+n['path']+'</guid><description>'+xml_escape(n['description'])+'</description></item>' for n in notes)
    (OUT/'feed.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Annan Chen</title><link>'+SITE+'</link><description>Projects and notes</description>'+items+'</channel></rss>',encoding='utf-8')
    report={'pages':len(PAGES),'languages':['zh','en'],'legacy_articles':7,'full_translations':sorted(set(translations)),'project_details':3,'notes':2,'legacy_routes':[i['path'] for i in legacy],'routes':list(PAGES),'paired_routes':list(META),'analytics_endpoint':ANALYTICS+'/api/collect'}
    (OUT/'build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
