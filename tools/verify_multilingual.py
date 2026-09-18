"""Regression tests: preservation, real section pages and cross-page anchors."""
from pathlib import Path
from urllib.parse import urlparse, unquote
import re
import build as b
from bs4 import BeautifulSoup

root=Path(b.ROOT)
raw=b.load_source()
def words(tag):
    return " ".join(tag.get_text(" ",strip=True).split())
checked=0
for lang in b.LANGS[1:]:
    source=b.prepared_soup(raw,lang)
    b.youtube_facade(source,lang)
    for p in b.CONTENT_PAGES+b.RECORDINGS:
        old=source.find(id=p["id"])
        b.strip_inpage_navs(old)
        new=BeautifulSoup((root/lang/p["slug"]/"index.html").read_text(),"html.parser").find(id=p["id"])
        if p["slug"]=="sprostowania":
            assert len(new.select(".errata-lista > li"))==7,(lang,"corrections")
            continue
        if p["slug"]=="pomoc-ukraincom":
            added=new.find(id="octopus")
            assert added is not None,(lang,"OCTOPUS missing")
            added.decompose()
        assert words(old)==words(new),(lang,p["slug"],"text changed")
        checked+=1
    home=BeautifulSoup((root/lang/"index.html").read_text(),"html.parser")
    before=len(words(source.body))
    after=len(words(home.body))
    reduction=1-after/before
    assert reduction>=.80,(lang,"home not shortened",reduction)
    assert len(home.find_all("audio"))==0
    print(lang,f"home reduction {reduction:.1%}",before,after)

cache={}
for rel in b.all_generated_paths():
    path=root/rel
    soup=BeautifulSoup(path.read_text(),"html.parser")
    for a in soup.find_all("a",href=True):
        u=urlparse(a["href"])
        if u.netloc or u.scheme or not u.fragment or u.fragment in b.NATIVE_FRAGMENTS:continue
        if not u.path: target=path
        elif u.path.startswith("/"):target=root/u.path.lstrip("/")
        else:target=path.parent/u.path
        if target.suffix.lower() not in ("",".html"):continue
        if target.suffix=="":target=target/"index.html"
        if target not in cache:
            dom=BeautifulSoup(target.read_text(),"html.parser")
            cache[target]={n["id"] for n in dom.find_all(id=True)}
        assert unquote(u.fragment) in cache[target],(rel,a["href"],"broken target")
print("Preserved",checked,"translated evidence sections; all cross-page anchors valid.")
