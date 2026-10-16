from __future__ import annotations
import datetime as dt, email.utils, html, json, os, re, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ARTICLES=ROOT/'articles'; DATA=ROOT/'data/designers.json'; ROT=ROOT/'data/rotation.json'
SITE_URL=os.getenv('SITE_URL','https://archivefourtytwo.github.io/daily-design-news').rstrip('/')
def esc(v): return html.escape(str(v),quote=True)
def fetch_news(q,limit=4):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':q,'hl':'en-GB','gl':'GB','ceid':'GB:en'})
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'DDN/2.0'}); root=ET.fromstring(urllib.request.urlopen(req,timeout=15).read()); out=[]
        for item in root.findall('./channel/item')[:limit]:
            title=(item.findtext('title') or '').strip(); link=(item.findtext('link') or '').strip(); pub=(item.findtext('pubDate') or '').strip(); src=item.find('source'); source=src.text.strip() if src is not None and src.text else 'Source'
            if title and link: out.append({'title':title,'link':link,'pub':pub,'source':source})
        return out
    except Exception as e: print('news fetch failed',e); return []
def refs(s,items):
    rows=[f'<a class="reference" href="{esc(s["url"])}" rel="noopener noreferrer"><strong>Official / primary source</strong><span>{esc(s["name"])}</span></a>']
    for i in items:
        try: d=email.utils.parsedate_to_datetime(i['pub']).strftime('%d %b %Y')
        except: d=''
        meta=' / '.join(x for x in [i['source'],d] if x); rows.append(f'<a class="reference" href="{esc(i["link"])}" rel="noopener noreferrer"><strong>{esc(i["title"])}</strong><span>{esc(meta)}</span></a>')
    return ''.join(rows)
def article(day,n,s,news):
    iso=day.isoformat(); canonical=f'{SITE_URL}/articles/{iso}-{s["slug"]}.html'; disclosure=''
    if s.get('self_feature'): disclosure='<div class="disclosure"><strong>Disclosure:</strong> DDN is published by Archive42. This is a self-feature and not independent third-party coverage.</div>'
    body=''.join(f'<p>{esc(p)}</p>' for p in s['body'])
    schema={'@context':'https://schema.org','@type':'Article','headline':f'{s["name"]} — DDN {n:03d}','datePublished':iso,'dateModified':iso,'mainEntityOfPage':canonical,'description':s['dek'],'publisher':{'@type':'Organization','name':'Daily Design News'}}
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(s['name'])} — DDN {n:03d}</title><meta name="description" content="{esc(s['dek'])}"><link rel="canonical" href="{esc(canonical)}"><link rel="stylesheet" href="../assets/style.css"><script type="application/ld+json">{json.dumps(schema)}</script></head><body><header class="site-header"><div class="header-inner"><a class="logo" href="../index.html">DDN<small>Daily Design News</small></a><nav><a href="../index.html">Index</a><a href="../about.html">About</a><a href="../feed.xml">RSS</a></nav></div></header><main><article class="article"><header class="article-header"><div class="eyebrow">DDN / {n:03d} / {day.strftime('%d.%m.%Y')}</div><h1>{esc(s['name'])}</h1><p class="standfirst">{esc(s['dek'])}</p><div class="article-meta"><span>{esc(s['type'])}</span><span>{esc(s['location'])}</span><a class="text-link" href="{esc(s['url'])}" rel="noopener noreferrer">Primary source ↗</a></div></header><section class="article-body">{body}{disclosure}</section><section><div class="section-title">References / current links</div><div class="references">{refs(s,news)}</div></section></article></main><footer><span>DDN / Weekly design index</span><span>Issue {n:03d}</span></footer></body></html>'''
def posts():
    out=[]
    for p in sorted(ARTICLES.glob('*.html'),reverse=True):
        m=re.match(r'(\d{4}-\d{2}-\d{2})-(.+)\.html',p.name)
        if not m: continue
        t=p.read_text(); h=re.search(r'<h1>(.*?)</h1>',t,re.S); ty=re.search(r'<div class="article-meta"><span>(.*?)</span>',t,re.S)
        out.append({'date':m.group(1),'file':p.name,'name':html.unescape(re.sub(r'<.*?>','',h.group(1)).strip()) if h else 'DDN','type':html.unescape(ty.group(1)) if ty else 'Feature'})
    return out
def rebuild(ps):
    latest=ps[0]; rows=''.join(f'<a class="issue-row" href="articles/{esc(p["file"])}"><span class="index-no">{len(ps)-i:03d}</span><h2>{esc(p["name"])}</h2><span class="type">{esc(p["type"])}</span><span class="arrow">↗</span></a>' for i,p in enumerate(ps))
    ROOT.joinpath('index.html').write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DDN — Daily Design News</title><meta name="description" content="A weekly independent index of designers, artists, studios and visual culture."><link rel="stylesheet" href="assets/style.css"></head><body><header class="site-header"><div class="header-inner"><a class="logo" href="index.html">DDN<small>Daily Design News</small></a><nav><a href="index.html">Index</a><a href="about.html">About</a><a href="feed.xml">RSS</a></nav></div></header><main><section class="hero"><div><div class="eyebrow">Independent design index / weekly</div><h1>Things worth looking at.</h1></div><div class="hero-copy"><p>Designers, artists, studios, moving image, visual systems and the spaces between them. One focused feature each week.</p><a class="text-link" href="articles/{latest['file']}">Latest / {esc(latest['name'])} ↗</a></div></section><section class="issue-index"><div class="index-head"><h2>Index</h2><p>One feature / every week</p></div>{rows}</section></main><footer><span>DDN / Daily Design News</span><span>Weekly since 2026</span></footer></body></html>''')
    items=[]
    for p in ps[:30]:
        link=f'{SITE_URL}/articles/{p["file"]}'; pub=email.utils.format_datetime(dt.datetime.fromisoformat(p['date']).replace(tzinfo=dt.timezone.utc)); items.append(f'<item><title>{esc(p["name"])}</title><link>{esc(link)}</link><guid>{esc(link)}</guid><pubDate>{pub}</pubDate></item>')
    ROOT.joinpath('feed.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>DDN — Daily Design News</title><link>{SITE_URL}</link><description>Weekly design index.</description>{"".join(items)}</channel></rss>')
    urls=[f'{SITE_URL}/',f'{SITE_URL}/about.html']+[f'{SITE_URL}/articles/{p["file"]}' for p in ps]; ROOT.joinpath('sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(u)}</loc></url>' for u in urls)+'</urlset>')
def main():
    ds={d['slug']:d for d in json.loads(DATA.read_text())}; rot=json.loads(ROT.read_text()); today=dt.date.fromisoformat(os.getenv('DDN_DATE',dt.date.today().isoformat())); existing=posts(); n=len(existing)+1; slug=os.getenv('DDN_DESIGNER') or rot[(n-1)%len(rot)]; s=ds[slug]; out=ARTICLES/f'{today.isoformat()}-{slug}.html'
    if not out.exists() or os.getenv('FORCE_REBUILD')=='1': out.write_text(article(today,n,s,fetch_news(s['search'])))
    rebuild(posts())
if __name__=='__main__': main()
