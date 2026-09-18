"""Split existing translations into matching pages without rewriting evidence."""
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup

UI = {
 "en": dict(home="Home", contents="Explore the archive", read="Read more", previous="Previous",
            next="Next", all="All in this section", related="Related pages", index="Archive index",
            translated="Translation of the Polish original", source="Polish original"),
 "fr": dict(home="Accueil", contents="Explorer les archives", read="Lire la suite", previous="Précédent",
            next="Suivant", all="Tout le dossier", related="Pages associées", index="Index des archives",
            translated="Traduction de l’original polonais", source="Original polonais"),
 "de": dict(home="Startseite", contents="Archiv erkunden", read="Weiterlesen", previous="Zurück",
            next="Weiter", all="Alle Beiträge in diesem Bereich", related="Verwandte Seiten", index="Archivverzeichnis",
            translated="Übersetzung des polnischen Originals", source="Polnisches Original"),
 "uk": dict(home="Головна", contents="Переглянути архів", read="Читати далі", previous="Попередня",
            next="Наступна", all="Усі матеріали розділу", related="Пов’язані сторінки", index="Покажчик архіву",
            translated="Переклад польського оригіналу", source="Польський оригінал"),
}
CHROME = {
    "en": ("Skip to content", "Main navigation", "Open menu", "Close preview", "Document preview", "Footer navigation"),
    "fr": ("Aller au contenu", "Navigation principale", "Ouvrir le menu", "Fermer l’aperçu", "Aperçu du document", "Navigation de pied de page"),
    "de": ("Zum Inhalt", "Hauptnavigation", "Menü öffnen", "Vorschau schließen", "Dokumentvorschau", "Fußnavigation"),
    "uk": ("Перейти до вмісту", "Основна навігація", "Відкрити меню", "Закрити перегляд", "Перегляд документа", "Навігація внизу сторінки"),
}


def route(lang, slug=""):
    return "/" + (lang + "/" if lang != "pl" else "") + (slug + "/" if slug else "")


def page_slugs(b):
    return [h["slug"] for h in b.HUBS] + [p["slug"] for p in b.CONTENT_PAGES+b.RECORDINGS] + ["skorowidz"]


def counterpart_links(b, soup, lang, slug):
    for a in soup.select(".lang-switcher a"):
        other = a.get("hreflang") or next(
            (l for l in b.LANGS if "nav-"+l in a.get("class",[])), None)
        # Existing switcher anchors carry the original language URL.
        if other not in b.LANGS:
            other = a.get("href","/").strip("/").split("/")[0] or "pl"
        a["href"] = route(other, slug)
        a["hreflang"] = other
        a["class"] = ["lang-btn"] + (["active"] if other == lang else [])
    for tag in list(soup.head.select('link[rel="alternate"][hreflang]')):
        tag.decompose()
    for other in b.LANGS + ["x-default"]:
        actual = "pl" if other == "x-default" else other
        link=soup.new_tag("link", rel="alternate", hreflang=other,
                          href=b.SITE+route(actual,slug))
        soup.head.append(link)


def build_translations(b):
    root=Path(b.ROOT)
    additions={lang:{
        "corrections_html":(root/"src/translations"/("corrections-"+lang+".html")).read_text(),
        "octopus_html":(root/"src/translations"/("octopus-"+lang+".html")).read_text()
    } for lang in b.LANGS[1:]}
    written=[]
    for lang in b.LANGS[1:]:
        text=UI[lang]
        original=BeautifulSoup((root/lang/"index.html").read_text(),"html.parser")
        sections={}
        labels={}
        idmap={}
        for p in b.CONTENT_PAGES+b.RECORDINGS:
            sec=deepcopy(original.find(id=p["id"]))
            b.expect(sec is not None,"missing translated section "+lang+"/"+p["slug"])
            b.strip_inpage_navs(sec)
            if p["slug"]=="sprostowania":
                sec=BeautifulSoup(additions[lang]["corrections_html"],"html.parser").find("section")
                for block in sec.select("[data-lang]"):
                    block["data-lang"]=lang
            elif p["slug"]=="pomoc-ukraincom":
                translated=BeautifulSoup(additions[lang]["octopus_html"],"html.parser").find("article")
                source_note=original.new_tag("p",attrs={"class":"rec-numbering"})
                source_note.append(text["translated"]+". ")
                source_link=original.new_tag("a",href="/pomoc-ukraincom/#octopus")
                source_link["hreflang"]="pl";source_link["data-original"]="pl"
                source_link.string=text["source"]+" (PL)"
                source_note.append(source_link);translated.append(source_note)
                block=sec.select_one('.lang-block') or sec
                block.append(translated)
            sections[p["slug"]]=sec
            heading=sec.find(["h1","h2"])
            b.expect(heading is not None,"empty translated page "+lang+"/"+p["slug"])
            labels[p["slug"]]=heading.get_text(" ",strip=True)
            for tag in [sec]+sec.find_all(id=True):
                if tag.get("id"):
                    idmap[tag["id"]]=(p["slug"],tag["id"]!=p["id"])
        navlabels={key:labels_by_lang[lang] for key,href,labels_by_lang in b.NAV_TABS}
        labels.update(navlabels)
        labels["skorowidz"]=b.SKOROWIDZ_META[lang][2]
        known=set(page_slugs(b))
        shell=deepcopy(original)
        for sec in list(shell.find_all("section")): sec.decompose()
        b.strip_inpage_navs(shell)
        shell.main.clear()

        def local_href(href, ids):
            parsed=urlparse(href)
            if parsed.scheme and parsed.netloc not in {"whistleblower.witekkilarski.org",
                "witekkilarski.org","www.witekkilarski.org"}: return href
            if parsed.netloc and not parsed.scheme: return href
            path=parsed.path
            if path.startswith("/docs/") or path.startswith("docs/"): return href
            if not path:
                if parsed.fragment in ids or parsed.fragment in b.NATIVE_FRAGMENTS: return href
                if parsed.fragment in idmap:
                    target,inner=idmap[parsed.fragment]
                    return route(lang,target)+("#"+parsed.fragment if inner else "")
                return href
            slug=path.strip("/")
            if slug.endswith("/index.html"):slug=slug[:-11]
            if slug=="index.html":slug=""
            for language in b.LANGS[1:]:
                if slug==language:slug=""
                elif slug.startswith(language+"/"):slug=slug[len(language)+1:]
            if not slug:
                if parsed.fragment in idmap:
                    target,inner=idmap[parsed.fragment]
                    return route(lang,target)+("#"+parsed.fragment if inner else "")
                return route(lang)+("#"+parsed.fragment if parsed.fragment else "")
            if slug in known:
                fragment=parsed.fragment
                # Preserve inner document anchors when there is a matching translated target.
                if fragment and fragment in idmap and idmap[fragment][0]==slug:
                    return route(lang,slug)+"#"+fragment
                return route(lang,slug)
            return href

        def breadcrumb(soup,slug):
            nav=soup.new_tag("nav",attrs={"class":"breadcrumb","aria-label":"Breadcrumb"})
            a=soup.new_tag("a",href=route(lang));a.string=text["home"];nav.append(a)
            group=b.GROUP_OF_SLUG.get(slug)
            if group in b.HUB_BY_SLUG:
                nav.append(" › ")
                a=soup.new_tag("a",href=route(lang,group));a.string=navlabels[group];nav.append(a)
            nav.append(" › "+labels[slug])
            return nav

        def related(soup,slug):
            siblings=b.hub_order(slug)
            nav=soup.new_tag("nav",attrs={"class":"rec-prevnext","aria-label":text["related"]})
            if slug in siblings:
                i=siblings.index(slug)
                if i:
                    a=soup.new_tag("a",href=route(lang,siblings[i-1]))
                    a.string="← "+text["previous"]+": "+labels[siblings[i-1]];nav.append(a)
                group=b.GROUP_OF_SLUG.get(slug)
                if group in b.HUB_BY_SLUG:
                    a=soup.new_tag("a",href=route(lang,group));a.string=text["all"];nav.append(a)
                if i+1<len(siblings):
                    a=soup.new_tag("a",href=route(lang,siblings[i+1]))
                    a.string=text["next"]+": "+labels[siblings[i+1]]+" →";nav.append(a)
            a=soup.new_tag("a",href=route(lang,"skorowidz"));a.string=text["index"];nav.append(a)
            return nav

        def save(soup,slug,title,description):
            soup.html["lang"]=lang
            canonical=b.SITE+route(lang,slug)
            b.set_head(soup,lang=lang,title=title,description=description,
                       page_url=canonical,hreflang_cluster=False,keep_faq=False)
            for key in ("article:modified_time",):
                tag=soup.select_one('meta[property="'+key+'"]')
                if tag:tag["content"]=b.BUILD_DATE
            if slug:
                crumbs=[{"@type":"ListItem","position":1,"name":text["home"],"item":b.SITE+route(lang)}]
                group=b.GROUP_OF_SLUG.get(slug)
                if group in b.HUB_BY_SLUG:
                    crumbs.append({"@type":"ListItem","position":2,"name":navlabels[group],
                                   "item":b.SITE+route(lang,group)})
                crumbs.append({"@type":"ListItem","position":len(crumbs)+1,
                               "name":labels[slug],"item":canonical})
                b.put_ld(soup,{"@context":"https://schema.org","@graph":[{
                    "@type":"Article","headline":title,"description":description,"inLanguage":lang,
                    "dateModified":b.BUILD_DATE,"author":{"@type":"Person","name":"Dr Witold Kilarski"},
                    "mainEntityOfPage":canonical},{"@type":"BreadcrumbList","itemListElement":crumbs}]})
            chrome=CHROME[lang]
            skip=soup.select_one(".skip-link")
            if skip:skip.string=chrome[0]
            for selector,label in [("#nav-links",chrome[1]),("#mobile-menu-btn",chrome[2]),
                                   ("#doc-modal-close",chrome[3]),(".footer-links",chrome[5])]:
                tag=soup.select_one(selector)
                if tag:tag["aria-label"]=label
            modal_title=soup.find(id="doc-modal-title")
            if modal_title:modal_title.string=chrome[4]
            soup.select_one(".header-logo")["href"]=route(lang)
            current=slug if slug in navlabels else b.GROUP_OF_SLUG.get(slug)
            for a in soup.select("#nav-links a"):
                key=a["data-nav"]
                a["href"]=route(lang,"" if key=="sprawa" else key)
                a.attrs.pop("aria-current",None)
                if key==(current or "sprawa"):a["aria-current"]="page"
            ids=b.page_ids(soup)
            for a in soup.find_all("a",href=True):
                if "lang-btn" not in (a.get("class") or []) and not a.get("data-original"):
                    a["href"]=local_href(a["href"],ids)
            counterpart_links(b,soup,lang,slug)
            b.normalize_headings(soup.body)
            b.clean_metadata(soup)
            dest=root/route(lang,slug).lstrip("/")/"index.html"
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_text(str(soup),encoding="utf-8")
            written.append(str(dest))

        for p in b.CONTENT_PAGES+b.RECORDINGS:
            slug=p["slug"]
            soup=deepcopy(shell)
            sec=deepcopy(sections[slug])
            b.promote_first_heading(sec)
            soup.main.append(breadcrumb(soup,slug))
            if slug=="sprostowania":
                note=soup.new_tag("p",attrs={"class":"rec-numbering"})
                note.append(text["translated"]+". ")
                a=soup.new_tag("a",href="/sprostowania/")
                a["hreflang"]="pl";a["data-original"]="pl";a.string=text["source"]+" (PL)"
                note.append(a);soup.main.append(note)
            soup.main.append(sec)
            soup.main.append(related(soup,slug))
            intro=sec.find("p")
            description=intro.get_text(" ",strip=True) if intro else labels[slug]
            save(soup,slug,labels[slug]+" | Witold Kilarski",description)

        for hub in b.HUBS:
            slug=hub["slug"]; soup=deepcopy(shell)
            wrap=soup.new_tag("div",attrs={"class":"hub-page"})
            wrap.append(breadcrumb(soup,slug))
            h=soup.new_tag("h1");h.string=navlabels[slug];wrap.append(h)
            ul=soup.new_tag("ul",attrs={"class":"hub-list"})
            items=[r["slug"] for r in b.RECORDINGS] if slug=="nagrania" else hub["items"]
            for item in items:
                li=soup.new_tag("li");a=soup.new_tag("a",href=route(lang,item))
                a["class"]=["hub-list-title"];a.string=labels[item];li.append(a);ul.append(li)
            wrap.append(ul);soup.main.append(wrap)
            save(soup,slug,navlabels[slug]+" | Witold Kilarski"," · ".join(labels[x] for x in items))

        # Retain every original index entry, changing only its destination.
        index=BeautifulSoup((root/lang/"skorowidz/index.html").read_text(),"html.parser")
        crumb=index.select_one(".breadcrumb")
        if crumb:crumb.replace_with(breadcrumb(index,"skorowidz"))
        save(index,"skorowidz",b.SKOROWIDZ_META[lang][0],b.SKOROWIDZ_META[lang][1])

        # Compact landing page: existing hero, case introduction and six cards.
        home=deepcopy(shell)
        hero=deepcopy(original.select_one("section.hero"))
        if hero:home.main.insert_before(hero)
        wrap=home.new_tag("section",id="home-hub")
        h=home.new_tag("h2");h.string=text["contents"];wrap.append(h)
        introductions=[p for p in sections["wprowadzenie"].find_all("p")
                       if not p.find_parent(class_="nn-definition")
                       and "nn-definition" not in p.get("class",[])
                       and not p.find_parent("blockquote")]
        for intro in introductions[:2]:
            wrap.append(deepcopy(intro))
        cards=home.new_tag("div",attrs={"class":"hub-cards"})
        for key,href,labs in b.NAV_TABS:
            slug="wprowadzenie" if key=="sprawa" else key
            card=home.new_tag("div",attrs={"class":"hub-card"})
            h=home.new_tag("h3");h.string=labs[lang];card.append(h)
            if slug in sections:
                p=home.new_tag("p");p.string=labels[slug];card.append(p)
            else:
                hub=b.HUB_BY_SLUG[slug]
                items=[r["slug"] for r in b.RECORDINGS] if slug=="nagrania" else hub["items"]
                p=home.new_tag("p");p.string=" · ".join(labels[x] for x in items[:3]);card.append(p)
            line=home.new_tag("p",attrs={"class":"hub-card-cta"})
            a=home.new_tag("a",href=route(lang,slug));a.string=text["read"]+" →"
            line.append(a);card.append(line);cards.append(card)
        wrap.append(cards);home.main.append(wrap)
        redirect={key:route(lang,slug)+("#"+key if inner else "")
                  for key,(slug,inner) in idmap.items()}
        b.install_anchor_redirect(home,redirect)
        save(home,"",b.LANG_META[lang][0],b.LANG_META[lang][1])

    # Every Polish page also links to its exact translated counterpart.
    for slug in [""]+page_slugs(b):
        dest=root/slug/"index.html"
        soup=BeautifulSoup(dest.read_text(),"html.parser")
        counterpart_links(b,soup,"pl",slug)
        dest.write_text(str(soup),encoding="utf-8")
    return written
