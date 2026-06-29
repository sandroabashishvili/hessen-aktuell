from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from html import unescape
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

from .http_client import fetch_text
from .models import NewsItem, NewsSource


MAX_ITEMS_PER_SOURCE = 5


def collect_source_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    if source.source_id == "stadt-kassel-aktuelles":
        return collect_stadt_kassel_items(source, day_iso)
    if source.source_id == "landkreis-kassel-presse":
        return collect_landkreis_kassel_items(source, day_iso)
    if source.source_id == "polizei-nordhessen-presse":
        return collect_polizei_nordhessen_items(source, day_iso)
    if source.source_id == "polizei-frankfurt-presse":
        return collect_presseportal_frankfurt_items(source, day_iso)
    if source.source_id == "vgf-frankfurt-news":
        return collect_vgf_frankfurt_items(source, day_iso)
    if source.source_id == "mainova-frankfurt-presse":
        return collect_mainova_frankfurt_items(source, day_iso)
    if source.source_id == "stadt-wiesbaden-presse":
        return collect_wiesbaden_presse_items(source, day_iso)
    if source.source_id == "polizei-wiesbaden-presse":
        return collect_presseportal_wiesbaden_items(source, day_iso)
    if source.source_id == "stadt-darmstadt-presse":
        return collect_darmstadt_presse_items(source, day_iso)
    if source.source_id == "polizei-darmstadt-presse":
        return collect_presseportal_darmstadt_items(source, day_iso)
    if source.source_id in {"hessen-government-presse", "hessen-economy-transport-presse"}:
        return collect_hessen_press_items(source, day_iso)
    return []


def collect_stadt_kassel_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_stadt_kassel_items(html, source, day_iso)


def collect_landkreis_kassel_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    xml = fetch_text(
        "https://www.landkreiskassel.de/pressemitteilungen/index.php"
        "?sp%3Aout=rss&sp%3Acmp=search-1-0-searchResult&action=submit"
    )
    if xml:
        items = parse_landkreis_kassel_rss_items(xml, source, day_iso)
        if items:
            return items
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_landkreis_kassel_items(html, source, day_iso)


def collect_polizei_nordhessen_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_polizei_nordhessen_items(html, source, day_iso)


def collect_presseportal_frankfurt_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    xml = fetch_text("https://www.presseportal.de/rss/dienststelle_4970.rss2?langid=1")
    if not xml:
        return []
    return parse_rss_items(xml, source, day_iso)


def collect_presseportal_wiesbaden_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    xml = fetch_text("https://www.presseportal.de/rss/polizei/r/Wiesbaden.rss2")
    if not xml:
        return []
    return parse_rss_items(xml, source, day_iso)


def collect_presseportal_darmstadt_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    xml = fetch_text("https://www.presseportal.de/rss/polizei/r/Darmstadt.rss2")
    if not xml:
        return []
    return parse_rss_items(xml, source, day_iso)


def collect_vgf_frankfurt_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_vgf_frankfurt_items(html, source, day_iso)


def collect_mainova_frankfurt_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_mainova_frankfurt_items(html, source, day_iso)


def collect_wiesbaden_presse_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    xml = fetch_text("https://www.wiesbaden.de/pressemitteilungen/?sp%3Aout=rss")
    if not xml:
        return []
    return parse_rss_items(xml, source, day_iso)


def collect_darmstadt_presse_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_darmstadt_presse_items(html, source, day_iso)


def collect_hessen_press_items(source: NewsSource, day_iso: str) -> list[NewsItem]:
    html = fetch_text(source.url)
    if not html:
        return []
    return parse_hessen_press_items(html, source, day_iso)


def parse_stadt_kassel_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    section = _extract_pressemitteilungen_section(html)
    if not section:
        return []

    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<li class="SP-TeaserList__item">(.*?)</li>', section, re.S):
        item = _parse_stadt_kassel_teaser(raw_item, source, fallback_day_iso)
        if not item or item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_landkreis_kassel_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    section = _extract_landkreis_search_result_section(html)
    if not section:
        return []

    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<li class="SP-TeaserList__item">(.*?)</li>', section, re.S):
        item = _parse_landkreis_kassel_teaser(raw_item, source, fallback_day_iso)
        if not item or item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_polizei_nordhessen_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    section = _extract_polizei_list_section(html)
    if not section:
        return []

    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<div class="article">(.*?)</article>\s*</div>', section, re.S):
        item = _parse_polizei_nordhessen_teaser(raw_item, source, fallback_day_iso)
        if not item or item.source_url in seen_urls:
            continue
        seen_urls.add(item.source_url)
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_rss_items(xml: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []

    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in root.findall("./channel/item"):
        title = _clean_text(raw_item.findtext("title") or "")
        link = _clean_text(raw_item.findtext("link") or "")
        description = _clean_text(raw_item.findtext("description") or "")
        pub_date = _clean_text(raw_item.findtext("pubDate") or "")
        if not title or not link or link in seen_urls:
            continue
        seen_urls.add(link)
        published_day = _normalize_rss_day(pub_date, fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=link,
            title=title,
            summary=_preview_text(description),
            topic=_map_general_topic(f"{title} {description}", source.topic),
            summary_status="rss_adapter_minimal",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_landkreis_kassel_rss_items(xml: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []

    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in root.findall("./channel/item"):
        title = _clean_text(raw_item.findtext("title") or "")
        link = _clean_text(raw_item.findtext("link") or "")
        description = _clean_text(raw_item.findtext("description") or "")
        pub_date = _clean_text(raw_item.findtext("pubDate") or "")
        if not title or not link or link in seen_urls:
            continue
        if ".media/" in link or _looks_like_media_download(title, link):
            continue
        seen_urls.add(link)
        published_day = _normalize_rss_day(pub_date, fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=link,
            title=title,
            summary=_preview_text(description),
            topic=_map_landkreis_topic(title, source.topic),
            summary_status="rss_adapter_filtered",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_vgf_frankfurt_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<article class="news-simple-list__item.*?</article>', html, re.S):
        datetime_value = _first_match(raw_item, r'<time datetime="([^"]+)"')
        href = _first_match(raw_item, r'<h2><a class="more"[^>]+href="([^"]+)"')
        title = _clean_text(_first_match(raw_item, r'<h2><a class="more"[^>]*>(.*?)</a></h2>'))
        teaser_text = _clean_text(_first_match(raw_item, r'<div class="teaser-text news-simple-list__teaser">.*?<p>(.*?)</p>'))
        if not href or not title:
            continue
        item_url = urljoin(source.url, unescape(href))
        if item_url in seen_urls:
            continue
        seen_urls.add(item_url)
        published_day = _normalize_day(datetime_value, "", fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=item_url,
            title=title,
            summary=_preview_text(teaser_text),
            topic=_map_general_topic(f"{title} {teaser_text}", source.topic),
            summary_status="html_adapter_minimal",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_mainova_frankfurt_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<div class="news-events-article"[^>]*>\s*<a href="([^"]+)">(.*?)</a>\s*</div>', html, re.S):
        href, body = raw_item
        title = _clean_text(_first_match(body, r'<h3 class="module-article__item-headline">(.*?)</h3>'))
        date_text = _clean_text(_first_match(body, r'<div class="module-article__date">\s*<p>(.*?)</p>'))
        summary = _clean_text(_first_match(body, r'<div class="module-article__item-text text-box">\s*<p>(.*?)</p>'))
        category_text = " ".join(re.findall(r'<div class="news-events-article__categories">(.*?)</div>', body, re.S))
        categories = _clean_text(category_text)
        if not href or not title:
            continue
        item_url = urljoin(source.url, unescape(href))
        if item_url in seen_urls:
            continue
        seen_urls.add(item_url)
        published_day = _normalize_mainova_day(date_text, fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=item_url,
            title=title,
            summary=_preview_text(summary),
            topic=_map_mainova_topic(f"{categories} {title} {summary}", source.topic),
            summary_status="html_adapter_minimal",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_darmstadt_presse_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<div class="article articletype-0 topnews".*?</div></a></div>', html, re.S):
        href = _first_match(raw_item, r'<a title="[^"]*" href="([^"]+)"')
        title = _clean_text(_first_match(raw_item, r'<a title="([^"]*)" href="[^"]+"'))
        date_text = _clean_text(_first_match(raw_item, r'<time[^>]*>.*?<span>(\d{2}\.\d{2}\.\d{4})</span>.*?</time>'))
        description = _clean_text(_first_match(raw_item, r'<div class="content" itemprop="description">\s*<p>(.*?)</p>'))
        if not href or not title:
            continue
        item_url = urljoin(source.url, unescape(href))
        if item_url in seen_urls:
            continue
        seen_urls.add(item_url)
        published_day = _normalize_day("", date_text, fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=item_url,
            title=title,
            summary=_preview_text(description),
            topic=_map_general_topic(f"{title} {description}", source.topic),
            summary_status="html_adapter_minimal",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def parse_hessen_press_items(html: str, source: NewsSource, fallback_day_iso: str) -> list[NewsItem]:
    items: list[NewsItem] = []
    seen_urls: set[str] = set()
    for raw_item in re.findall(r'<article about="[^"]+" class="node hw-article.*?</article>', html, re.S):
        href = _first_match(raw_item, r'<a class="teaser--area-link[^"]*"[^>]+href="([^"]+)"')
        title = _clean_text(_first_match(raw_item, r'<h2 class="teaser-generic__field-pt-headline[^"]*">(.*?)</h2>'))
        date_text = _clean_text(_first_match(raw_item, r'<p class="date my-0">(.*?)</p>'))
        dateline = _clean_text(_first_match(raw_item, r'<p class="teaser-generic__field-pt-dateline[^"]*">(.*?)</p>'))
        teaser_text = _clean_text(_first_match(raw_item, r'<div class="teaser-generic__field-pt-teasertext[^"]*">\s*<p>(.*?)</p>'))

        if not href or not title:
            continue
        item_url = urljoin(source.url, unescape(href))
        if item_url in seen_urls:
            continue
        seen_urls.add(item_url)
        published_day = _normalize_day("", date_text, fallback_day_iso)
        item = _build_item(
            source=source,
            published_day=published_day,
            item_url=item_url,
            title=title,
            summary=_preview_text(teaser_text),
            topic=_map_general_topic(f"{dateline} {title} {teaser_text}", source.topic),
            summary_status="html_adapter_minimal",
        )
        items.append(item)
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def _extract_pressemitteilungen_section(html: str) -> str:
    match = re.search(
        r'<h2[^>]+id="pressemitteilungen"[^>]*>.*?</h2>.*?<ul class="SP-TeaserList__list">(.*?)</ul>',
        html,
        re.S,
    )
    return match.group(1) if match else ""


def _extract_landkreis_search_result_section(html: str) -> str:
    match = re.search(
        r'<h2 class="SP-Search__result__headline__inner">Aktuelles aus dem Landkreis Kassel</h2>.*?'
        r'<ul class="SP-TeaserList__list">(.*?)</ul>',
        html,
        re.S,
    )
    return match.group(1) if match else ""


def _extract_polizei_list_section(html: str) -> str:
    match = re.search(r'<div id="hw_core_list"[^>]*>(.*?)<nav[^>]+aria-label="Seitennavigation"', html, re.S)
    if match:
        return match.group(1)
    fallback = re.search(r'<div id="hw_core_list"[^>]*>(.*?)(?:<footer|</main>)', html, re.S)
    return fallback.group(1) if fallback else ""


def _parse_stadt_kassel_teaser(raw_item: str, source: NewsSource, fallback_day_iso: str) -> NewsItem | None:
    datetime_value = _first_match(raw_item, r'<time[^>]+datetime="([^"]+)"')
    date_text = _first_match(raw_item, r'<span class="SP-Scheduling__date">(.*?)</span>')
    category = _clean_text(_first_match(raw_item, r'<span class="SP-Kicker__category">(.*?)</span>'))
    href = _first_match(raw_item, r'<a class="SP-Teaser__link"[^>]+href="([^"]+)"')
    title = _clean_text(_first_match(raw_item, r'<span class="SP-Teaser__headline__text">(.*?)</span>'))
    teaser_text = _clean_text(_first_match(raw_item, r'<div class="SP-Teaser__abstract">(.*?)</div>'))

    if not href or not title:
        return None

    published_day = _normalize_day(datetime_value, date_text, fallback_day_iso)
    item_topic = _map_kassel_category(category, title, source.topic)
    item_url = urljoin(source.url, unescape(href))
    return _build_item(source, published_day, item_url, title, _preview_text(teaser_text), item_topic, "html_adapter_minimal")


def _parse_landkreis_kassel_teaser(raw_item: str, source: NewsSource, fallback_day_iso: str) -> NewsItem | None:
    category = _clean_text(_first_match(raw_item, r'<span class="SP-Kicker__category">(.*?)</span>'))
    if category.lower() != "pressemitteilung":
        return None

    href = _first_match(raw_item, r'<a class="SP-Teaser__link"[^>]+href="([^"]+)"')
    title = _clean_text(_first_match(raw_item, r'<span class="SP-Teaser__headline__text">(.*?)</span>'))
    teaser_text = _clean_text(_first_match(raw_item, r'<div class="SP-Teaser__abstract">(.*?)</div>'))
    if not href or not title or ".media/" in href:
        return None

    datetime_value = _first_match(raw_item, r'<time[^>]+datetime="([^"]+)"')
    date_text = _first_match(raw_item, r'<span class="SP-Scheduling__date">(.*?)</span>')
    published_day = _normalize_day(datetime_value, date_text, fallback_day_iso)
    item_topic = _map_landkreis_topic(title, source.topic)
    item_url = urljoin(source.url, unescape(href))
    return _build_item(source, published_day, item_url, title, _preview_text(teaser_text), item_topic, "html_adapter_minimal")


def _parse_polizei_nordhessen_teaser(raw_item: str, source: NewsSource, fallback_day_iso: str) -> NewsItem | None:
    href = _first_match(raw_item, r'<a class="teaser--area-link[^"]*"[^>]+href="([^"]+)"')
    title = _clean_text(_first_match(raw_item, r'<h2 class="teaser-generic__field-pt-headline[^"]*">(.*?)</h2>'))
    date_text = _first_match(raw_item, r'<p class="date my-0">(.*?)</p>')
    teaser_text = _clean_text(_first_match(raw_item, r'<div class="teaser-generic__field-pt-teasertext[^"]*">\s*<p>(.*?)</p>'))

    if not href or not title:
        return None

    published_day = _normalize_day("", date_text, fallback_day_iso)
    item_url = urljoin(source.url, unescape(href))
    return _build_item(source, published_day, item_url, title, _preview_text(teaser_text), source.topic, "html_adapter_minimal")


def _build_item(
    source: NewsSource,
    published_day: str,
    item_url: str,
    title: str,
    summary: str,
    topic: str,
    summary_status: str,
) -> NewsItem:
    return NewsItem(
        item_id=f"{source.source_id}-{_slug_from_url(item_url)}",
        title=title,
        summary=summary,
        source_name=source.name,
        source_url=item_url,
        source_family=source.family,
        city=source.city,
        topic=topic,
        published_date=published_day,
        summary_status=summary_status,
        image_rights_status=source.image_policy,
        media_type="placeholder",
        media_url=None,
        media_source="local_placeholder",
        media_rights_status=source.image_policy,
        image_download_allowed=source.image_download_allowed,
        youtube_embed_allowed=source.youtube_embed_allowed,
    )


def _map_kassel_category(category: str, title: str, fallback_topic: str) -> str:
    normalized = f"{category} {title}".lower()
    if any(token in normalized for token in ("baustelle", "verkehr", "straße", "strasse", "mobilität")):
        return "Transport"
    if any(token in normalized for token in ("veranstaltung", "ferien", "programm", "kultur")):
        return "Events"
    if any(token in normalized for token in ("stavo", "ortsbeirat", "beirat", "stadtpolitik", "gremien")):
        return "Politics"
    if any(token in normalized for token in ("polizei", "feuerwehr", "einsatz")):
        return "Police"
    return fallback_topic


def _map_landkreis_topic(title: str, fallback_topic: str) -> str:
    normalized = title.lower()
    if any(token in normalized for token in ("verkehr", "straße", "strasse", "mobilität", "bus", "bahn")):
        return "Transport"
    if any(token in normalized for token in ("ferien", "konzert", "veranstaltung", "programm", "kultur")):
        return "Events"
    if any(token in normalized for token in ("investition", "kreistag", "landrat", "verwaltung", "arbeitsbedingungen")):
        return "Politics"
    if any(token in normalized for token in ("hitze", "gesundheit", "klima", "naturschutz", "umwelt")):
        return "Safety"
    return fallback_topic


def _map_general_topic(text: str, fallback_topic: str) -> str:
    normalized = text.lower()
    if any(token in normalized for token in ("polizei", "festnahme", "zeugen", "raub", "einbruch", "betrug", "verletzte")):
        return "Police"
    if any(token in normalized for token in ("straße", "strasse", "verkehr", "bus", "bahn", "mobilität", "fernwärme")):
        return "Transport"
    if any(token in normalized for token in ("wahl", "stadtverordnet", "kommunal", "haushalt", "finanz")):
        return "Politics"
    if any(token in normalized for token in ("klima", "gesund", "wasser", "hitze", "sicherheit")):
        return "Safety"
    if any(token in normalized for token in ("kita", "ferien", "vortrag", "veranstaltung", "kultur")):
        return "Events"
    return fallback_topic


def _map_mainova_topic(text: str, fallback_topic: str) -> str:
    normalized = text.lower()
    if any(token in normalized for token in ("baustelle", "leitung", "fernwärme", "fernwaerme", "straße", "strasse", "netze")):
        return "Transport"
    if any(token in normalized for token in ("mainova", "aufsichtsrat", "vorstand", "unternehmen", "geschäft", "geschaeft")):
        return "Economy"
    if any(token in normalized for token in ("klima", "strom", "energie", "wärme", "waerme", "laden", "emobilität", "elektro")):
        return "Safety"
    if any(token in normalized for token in ("aktion", "verein", "engagement", "sport")):
        return "Events"
    return fallback_topic


def _preview_text(value: str, max_chars: int = 320) -> str:
    cleaned = value.strip()
    if not cleaned:
        return ""
    if len(cleaned) <= max_chars:
        return cleaned
    trimmed = cleaned[: max_chars - 1].rsplit(" ", 1)[0].rstrip(" .,;:")
    return f"{trimmed}."


def _normalize_day(datetime_value: str, date_text: str, fallback_day_iso: str) -> str:
    if datetime_value:
        try:
            return datetime.fromisoformat(datetime_value.replace("Z", "+00:00")).date().isoformat()
        except ValueError:
            pass
    if date_text:
        try:
            return datetime.strptime(date_text.strip(), "%d.%m.%Y").date().isoformat()
        except ValueError:
            pass
    return fallback_day_iso


def _normalize_rss_day(pub_date: str, fallback_day_iso: str) -> str:
    if not pub_date:
        return fallback_day_iso
    try:
        return parsedate_to_datetime(pub_date).date().isoformat()
    except (TypeError, ValueError, IndexError):
        return fallback_day_iso


def _normalize_mainova_day(date_text: str, fallback_day_iso: str) -> str:
    date_part = date_text.split("|", 1)[0].strip()
    return _normalize_day("", date_part, fallback_day_iso)


def _first_match(value: str, pattern: str) -> str:
    match = re.search(pattern, value, re.S)
    return match.group(1) if match else ""


def _clean_text(value: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", value)
    cleaned = unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _slug_from_url(url: str) -> str:
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    slug = slug.removesuffix(".php")
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower() or "item"


def _looks_like_media_download(title: str, url: str) -> bool:
    normalized = f"{title} {url}".lower()
    return any(
        token in normalized
        for token in (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".pdf",
            ".doc",
            ".docx",
            ".zip",
        )
    )
