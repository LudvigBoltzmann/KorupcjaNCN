"""Publication-only metadata cleanup. Never edits visible evidence or documents."""
import json
from urllib.parse import urljoin, urlparse
from bs4 import Comment

EXCLUDE_PATHS = ("src", "tools", "backup", "raport", "site-content.json")

HOME_META = {
    "pl": ("NCN: archiwum dowodów sygnalisty | Witold Kilarski",
           "Nagrania, dokumenty i chronologia sprawy dr. Witolda Kilarskiego dotyczącej domniemanych nieprawidłowości w NCN oraz programu NAWA Polskie Powroty."),
    "en": ("NCN: whistleblower evidence archive | Witold Kilarski",
           "Recordings, documents and a timeline of Dr Witold Kilarski’s case concerning alleged irregularities at Poland’s NCN and the NAWA Polish Returns programme."),
    "fr": ("NCN : archives d’un lanceur d’alerte | Witold Kilarski",
           "Enregistrements, documents et chronologie de l’affaire du Dr Witold Kilarski concernant des irrégularités présumées au NCN et le programme NAWA."),
    "de": ("NCN: Beweisarchiv eines Whistleblowers | Witold Kilarski",
           "Aufnahmen, Dokumente und Chronologie zum Fall von Dr. Witold Kilarski: mutmaßliche Unregelmäßigkeiten beim NCN und im NAWA-Rückkehrprogramm."),
    "uk": ("NCN: архів доказів викривача | Witold Kilarski",
           "Записи, документи та хронологія справи д-ра Вітольда Кілярського щодо ймовірних порушень у NCN та програмі NAWA «Польські повернення»."),
}


def clean_metadata(soup):
    canonical = soup.select_one('link[rel="canonical"]')["href"]
    lang = soup.html.get("lang", "pl")
    is_home = urlparse(canonical).path in ("/", "/en/", "/fr/", "/de/", "/uk/")
    title = soup.title.get_text()
    description = soup.select_one('meta[name="description"]')["content"]
    if is_home:
        title, description = HOME_META[lang]
    elif len(title) > 70:
        # Remove boilerplate only, never truncate evidence names or qualifiers.
        title = title.removesuffix(" | Dr Witold Kilarski")
    soup.title.string = title
    for selector, value in (
        ('meta[name="description"]', description),
        ('meta[property="og:title"]', title),
        ('meta[name="twitter:title"]', title),
        ('meta[property="og:description"]', description),
        ('meta[name="twitter:description"]', description),
    ):
        tag = soup.select_one(selector)
        if tag:
            tag["content"] = value

    for tag in list(soup.head.find_all("meta")):
        name = (tag.get("name") or "").lower()
        prop = tag.get("property") or ""
        if (name in {"keywords", "news_keywords", "subject", "rating"}
                or name.startswith(("dc.", "geo."))
                or prop in {"article:tag", "article:section", "article:published_time"}):
            tag.decompose()
    for link in list(soup.head.find_all("link")):
        rel = set(link.get("rel") or [])
        if ("index-now" in rel or
                (rel & {"preconnect", "dns-prefetch"} and
                 "youtube.com" in link.get("href", ""))):
            link.decompose()
    for comment in list(soup.head.find_all(string=lambda x: isinstance(x, Comment))):
        if any(text in str(comment) for text in ("FAQPage", "boosts visibility", "IndexNow key reference")):
            comment.extract()

    graph = []
    audio_duration = None
    for script in list(soup.select('script[type="application/ld+json"]')):
        data = json.loads(script.string)
        for node in data.get("@graph", [data]):
            kind = node.get("@type")
            if kind == "AudioObject":
                audio_duration = node.get("duration", audio_duration)
                continue
            if kind == "FAQPage":
                continue
            if kind == "Article":
                # The original archive date is not a verified publication date
                # for every later page. Do not manufacture per-page dates.
                node.pop("datePublished", None)
                node["headline"] = title
                node["description"] = description
                node["inLanguage"] = lang
                node["mainEntityOfPage"] = canonical
            if kind == "Person":
                # Biography remains visible; avoid conflating degrees and jobs.
                node.pop("alumniOf", None)
            graph.append(node)
        script.decompose()

    players = soup.find_all("audio")
    for index, audio in enumerate(players, 1):
        source = audio.find("source", src=True)
        src = audio.get("src") or (source.get("src") if source else None)
        if not src:
            continue
        container = audio.find_parent("section")
        heading = container.find(["h1", "h2"]) if container else soup.h1
        name = heading.get_text(" ", strip=True) if heading else title
        player_box = audio.find_parent(class_="audio-player")
        player_title = player_box.find(class_="audio-player-title") if player_box else None
        if player_title:
            name = player_title.get_text(" ", strip=True)
        url = urljoin(canonical, src)
        node = {
            "@type": "AudioObject", "name": name, "inLanguage": "pl",
            "contentUrl": url, "url": canonical,
            "encodingFormat": (source.get("type") if source else None) or "audio/mpeg",
        }
        if len(players) == 1 and audio_duration:
            node["duration"] = audio_duration
        graph.append(node)
    script = soup.new_tag("script", attrs={"type": "application/ld+json"})
    script.string = "\n" + json.dumps({"@context": "https://schema.org", "@graph": graph},
                                    ensure_ascii=False, indent=2) + "\n"
    soup.head.append(script)
