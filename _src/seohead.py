# -*- coding: utf-8 -*-
import io,json,re,os,shutil

SITE='https://newfor.jp'
NAME='NEWFOR'
DESC_SITE='うまくいかなかったように見える挑戦にも、次の事業へ渡されたバトンがある。それを一件ずつ掘り起こして記録し、この国の新規事業の成功率を上げていく。そのための新規事業メディアです。'

# src -> (dist path, url path, title, desc, ogimg, type)
#
# ここは、サイトを作り始めたころの手書きHTMLを変換するための表でした。
# いまは同じページを、それぞれ専用の生成元が作っています。
#
#   /companies/            … 手で管理（gh/companies/index.html）
#   /companies/<slug>/     … mkcomp.py が companies/*.py から作る
#   /articles/<slug>/      … buildarticles.py が articles/a0*.py から作る
#
# 表に残しておくと、古い手書きHTML（12社226件・KDDI18事業のころ）から
# 同じ場所を作り直してしまい、公開中のページを古い内容で上書きします。
# 実際に llms.txt で同じ事故が起きました。だから空にしてあります。増やさないでください。
PAGES = {}

LINKMAP = {
 'newfor-top-light.html':'/', 'newfor-top.html':'/',
 'newfor-companies.html':'/companies/',
 'newfor-company-kddi.html':'/companies/kddi/',
 'newfor-site.html':'/articles/docomo-newbusiness/',
}

FAV = ('<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">\n'
 '<link rel="icon" href="/assets/favicon-32.png" sizes="32x32" type="image/png">\n'
 '<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">\n'
 '<link rel="manifest" href="/site.webmanifest">\n')

def org_ld():
    return {"@type":"Organization","@id":SITE+"/#org","name":NAME,"alternateName":"ニューフォー",
      "url":SITE+"/","logo":{"@type":"ImageObject","url":SITE+"/assets/apple-touch-icon.png","width":180,"height":180},
      "description":DESC_SITE}

def website_ld():
    return {"@type":"WebSite","@id":SITE+"/#site","url":SITE+"/","name":NAME,
      "inLanguage":"ja","description":DESC_SITE,"publisher":{"@id":SITE+"/#org"},
      "potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint",
        "urlTemplate":SITE+"/companies/?q={search_term_string}"},"query-input":"required name=search_term_string"}}

def person_ld():
    return {"@type":"Person","@id":SITE+"/#author","name":"Soichiro","alternateName":"新規事業マニア",
      "jobTitle":"事業開発","description":"20年にわたり事業の立ち上げに携わる。20代でスタートアップを立ち上げ1社を上場企業へ売却。その後、外資コンサル、通信大手、大手人材グループ、国内大手ITサービスの中で新規事業を立ち上げ、顧問として10社近くの新規事業を担当。",
      "knowsAbout":["新規事業","事業開発","社内起業","オープンイノベーション","CVC"],
      "worksFor":{"@id":SITE+"/#org"}}

def crumbs(items):
    return {"@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":i+1,"name":n,"item":SITE+u} for i,(n,u) in enumerate(items)]}

def build_ld(src,p):
    g=[org_ld(),website_ld(),person_ld()]
    if src=='newfor-top-light.html':
        g.append({"@type":"CollectionPage","@id":SITE+"/#webpage","url":SITE+"/","name":p['title'],
                  "description":p['desc'],"isPartOf":{"@id":SITE+"/#site"},"inLanguage":"ja"})
    elif src=='newfor-companies.html':
        g.append({"@type":"CollectionPage","@id":SITE+p['url']+"#webpage","url":SITE+p['url'],
                  "name":p['title'],"description":p['desc'],"isPartOf":{"@id":SITE+"/#site"},"inLanguage":"ja"})
        g.append(crumbs([("NEWFOR","/"),("大企業の新規事業","/companies/")]))
        g.append({"@type":"Dataset","name":"大企業の新規事業データベース",
          "description":"大企業が公開情報で発表した新規事業を、企業ごとに記録したデータセット。新規事業発表数・投資額・提携数を含む。",
          "url":SITE+"/companies/","creator":{"@id":SITE+"/#org"},"inLanguage":"ja",
          "temporalCoverage":"2015-01/2026-07","license":SITE+"/ads/"})
    elif src=='newfor-company-kddi.html':
        g.append({"@type":"WebPage","@id":SITE+p['url']+"#webpage","url":SITE+p['url'],
                  "name":p['title'],"description":p['desc'],"isPartOf":{"@id":SITE+"/#site"},"inLanguage":"ja",
                  "about":{"@type":"Corporation","name":"KDDI株式会社"}})
        g.append(crumbs([("NEWFOR","/"),("大企業の新規事業","/companies/"),("KDDI","/companies/kddi/")]))
    else:
        g.append({"@type":"Article","@id":SITE+p['url']+"#article","headline":"NTTドコモは、25年かけて「iモード」に帰ってきたのではないか",
          "description":p['desc'],"image":SITE+p['img'],"datePublished":"2026-07-28","dateModified":"2026-08-04",
          "author":{"@id":SITE+"/#author"},"publisher":{"@id":SITE+"/#org"},
          "mainEntityOfPage":SITE+p['url'],"inLanguage":"ja","articleSection":"新規事業ヒストリー",
          "keywords":"NTTドコモ,新規事業,iモード,dポイント,新規事業ヒストリー,事業開発","about":{"@type":"Corporation","name":"株式会社NTTドコモ"}})
        g.append(crumbs([("NEWFOR","/"),("記事一覧","/articles/"),("NTTドコモ","/articles/docomo-newbusiness/")]))
    return {"@context":"https://schema.org","@graph":g}

def head_block(src,p):
    u=SITE+p['url']; img=SITE+p['img']
    h=[]
    h.append('<link rel="canonical" href="%s">'%u)
    h.append('<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">')
    h.append('<meta name="author" content="Soichiro">')
    h.append('<meta name="theme-color" content="#2F3BD6" media="(prefers-color-scheme: light)">')
    h.append('<meta name="theme-color" content="#08080B" media="(prefers-color-scheme: dark)">')
    h.append('<meta property="og:type" content="%s">'%p['type'])
    h.append('<meta property="og:site_name" content="NEWFOR">')
    h.append('<meta property="og:locale" content="ja_JP">')
    h.append('<meta property="og:url" content="%s">'%u)
    h.append('<meta property="og:title" content="%s">'%p['title'])
    h.append('<meta property="og:description" content="%s">'%p['desc'])
    h.append('<meta property="og:image" content="%s">'%img)
    h.append('<meta property="og:image:width" content="1200">')
    h.append('<meta property="og:image:height" content="630">')
    h.append('<meta property="og:image:alt" content="NEWFOR ─ 新規事業ヒストリーメディア">')
    if p['type']=='article':
        h.append('<meta property="article:published_time" content="2026-07-28T09:00:00+09:00">')
        h.append('<meta property="article:modified_time" content="2026-08-04T09:00:00+09:00">')
        h.append('<meta property="article:author" content="Soichiro">')
        h.append('<meta property="article:section" content="新規事業ヒストリー">')
    h.append('<meta name="twitter:card" content="summary_large_image">')
    h.append('<meta name="twitter:title" content="%s">'%p['title'])
    h.append('<meta name="twitter:description" content="%s">'%p['desc'])
    h.append('<meta name="twitter:image" content="%s">'%img)
    h.append(FAV.rstrip())
    h.append('<script type="application/ld+json">%s</script>'%json.dumps(build_ld(src,p),ensure_ascii=False,separators=(',',':')))
    return '\n'.join(h)+'\n'

if __name__=='__main__':
    print(head_block('newfor-site.html',PAGES['newfor-site.html'])[:400])
