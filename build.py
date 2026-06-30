#!/usr/bin/env python3
"""간다GO 은평 출장마사지 — 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime

from content import PAGES
from content.site import (BASE_URL, BRAND, NAV, PHONE, PHONE_DISPLAY,
                          NAVER_VERIFICATION, GOOGLE_VERIFICATION, INDEXNOW_KEY)
from content.reviews_data import (REVIEWS, REVIEW_COUNT, RATING_VALUE,
                                  RATING_BEST, RATING_WORST)

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000
BUILD_DATE = datetime.date.today().isoformat()


def verification_meta() -> str:
    tags = []
    if NAVER_VERIFICATION:
        tags.append(f'<meta name="naver-site-verification" content="{NAVER_VERIFICATION}">')
    if GOOGLE_VERIFICATION:
        tags.append(f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">')
    return "\n".join(tags) + ("\n" if tags else "")


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


# ────────────────────────────────────────────────────────────
#  구조화 데이터(JSON-LD) — 페이지 종류별 일괄 생성
# ────────────────────────────────────────────────────────────
BASE = BASE_URL.rstrip("/")
_TEL = PHONE
_OG_IMG = f"{BASE}/assets/og-image.png"

# 사이트 전역 사업자 식별 정보 (모든 LocalBusiness 노드의 공통 골격)
_BIZ_CORE = {
    "@type": "HealthAndBeautyBusiness",
    "name": BRAND,
    "telephone": _TEL,
    "image": _OG_IMG,
    "priceRange": "₩90,000 - ₩180,000",
    "openingHoursSpecification": {
        "@type": "OpeningHoursSpecification",
        "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                      "Friday", "Saturday", "Sunday"],
        "opens": "00:00", "closes": "23:59",
    },
    "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 은평구"},
}

_AGG_RATING = {
    "@type": "AggregateRating",
    "ratingValue": RATING_VALUE,
    "reviewCount": str(REVIEW_COUNT),
    "bestRating": RATING_BEST,
    "worstRating": RATING_WORST,
}


def _jsonld(obj) -> str:
    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return f'<script type="application/ld+json">{data}</script>\n'


def _faq_from_body(body: str):
    """본문의 <div class="faq-item"><h3>Q</h3><p>A</p></div> 블록을 FAQPage로 변환."""
    items = re.findall(
        r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>',
        body, flags=re.S)
    qa = []
    for q, a in items:
        q = html.unescape(re.sub(r"<[^>]+>", "", q)).strip()
        a = html.unescape(re.sub(r"<[^>]+>", "", a)).strip()
        if q and a:
            qa.append({
                "@type": "Question", "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
    return qa


def _breadcrumb_ld(crumbs, canonical):
    elements = [{"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"}]
    pos = 2
    for label, href in crumbs:
        item = (BASE + href) if href else canonical
        elements.append({"@type": "ListItem", "position": pos, "name": label, "item": item})
        pos += 1
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": elements}


def _reviews_ld():
    out = []
    for r in REVIEWS:
        out.append({
            "@type": "Review",
            "author": {"@type": "Person", "name": r["name"]},
            "datePublished": r["date"],
            "reviewRating": {"@type": "Rating", "ratingValue": str(r["rating"]),
                             "bestRating": "5", "worstRating": "1"},
            "reviewBody": r["text"],
            "itemReviewed": {"@type": "Service", "name": f"{r['theme']} 방문 관리"},
        })
    return out


def structured_data(page: dict, path: str, canonical: str, noindex: bool) -> str:
    """페이지 경로에 맞춰 JSON-LD 스크립트 묶음을 생성한다."""
    blocks = []
    crumbs = page.get("breadcrumb") or []

    # 1) BreadcrumbList — 경로가 있는 모든 페이지
    if crumbs:
        blocks.append(_jsonld(_breadcrumb_ld(crumbs, canonical)))

    # 2) FAQPage — 본문에 FAQ 블록이 있으면 자동
    qa = _faq_from_body(page.get("body", ""))
    if qa and not noindex:
        blocks.append(_jsonld({"@context": "https://schema.org",
                               "@type": "FAQPage", "mainEntity": qa}))

    # 매거진 글은 자체 Article 스키마(extra_head)를 쓰므로 사업자 노드는 생략
    if path.startswith("magazine/") and path != "magazine/":
        return "".join(blocks)

    # 3) 테마 상세 → Service
    if path.startswith("themes/") and path != "themes/":
        name = crumbs[-1][0] if crumbs else page.get("h1", "")
        blocks.append(_jsonld({
            "@context": "https://schema.org", "@type": "Service",
            "serviceType": f"{name} 출장마사지·홈타이",
            "name": f"은평 {name} 방문 관리",
            "url": canonical,
            "areaServed": {"@type": "AdministrativeArea", "name": "서울특별시 은평구"},
            "provider": {**_BIZ_CORE, "url": BASE + "/", "aggregateRating": _AGG_RATING},
            "offers": {
                "@type": "AggregateOffer", "priceCurrency": "KRW",
                "lowPrice": "90000", "highPrice": "180000",
                "offerCount": "3",
            },
        }))
        return "".join(blocks)

    # 4) 그 외 페이지 → LocalBusiness 노드 (홈/지역/역/안내 공통)
    biz = {"@context": "https://schema.org", **_BIZ_CORE,
           "url": canonical, "aggregateRating": _AGG_RATING}

    if path == "":  # 홈 — WebSite + 대표 LocalBusiness
        biz["description"] = "은평구 전지역 방문 출장마사지·홈타이 예약 안내"
        biz["@id"] = BASE + "/#business"
        blocks.append(_jsonld({"@context": "https://schema.org", "@type": "WebSite",
                               "name": BRAND, "url": BASE + "/",
                               "inLanguage": "ko"}))
        blocks.append(_jsonld(biz))
    elif path.startswith("eunpyeong/") and path not in ("eunpyeong/", "eunpyeong/stations/"):
        # 지역·역 상세 — 해당 동/역을 areaServed 로 명시
        name = crumbs[-1][0] if crumbs else page.get("h1", "")
        biz["areaServed"] = [
            {"@type": "AdministrativeArea", "name": "서울특별시 은평구"},
            {"@type": "Place", "name": f"서울특별시 은평구 {name} 일대"},
        ]
        biz["description"] = page.get("desc", "")
        blocks.append(_jsonld(biz))
    elif path == "reviews/":
        biz["review"] = _reviews_ld()
        blocks.append(_jsonld(biz))
    else:
        biz["description"] = page.get("desc", "")
        blocks.append(_jsonld(biz))

    return "".join(blocks)


# ────────────────────────────────────────────────────────────
#  내부 링크 강화 — 롱테일 주제 관련 링크 블록
# ────────────────────────────────────────────────────────────
_RL_THEMES = [
    ("스웨디시", "/themes/swedish/"),
    ("아로마", "/themes/aroma/"),
    ("홈타이(타이마사지)", "/themes/thai/"),
    ("스포츠·경락", "/themes/sports/"),
    ("발마사지", "/themes/foot/"),
    ("커플 마사지", "/themes/couple/"),
    ("24시간 출장", "/themes/24hours/"),
    ("수면 가능", "/themes/overnight/"),
]
_RL_AREAS = [
    ("불광동", "/eunpyeong/bulgwang-dong/"),
    ("응암동", "/eunpyeong/eungam-dong/"),
    ("연신내·대조동", "/eunpyeong/daejo-dong/"),
    ("진관동(은평뉴타운)", "/eunpyeong/jingwan-dong/"),
    ("녹번동", "/eunpyeong/nokbeon-dong/"),
    ("역촌동", "/eunpyeong/yeokchon-dong/"),
]


def _chip(label, href):
    return f'<li><a href="{href}">{label}</a></li>'


def related_block(page: dict, path: str) -> str:
    """페이지 종류에 맞는 롱테일 내부 링크 블록(UI 카드)을 만든다."""
    crumbs = page.get("breadcrumb") or []
    subject = crumbs[-1][0] if crumbs else ""
    chips = []

    if path.startswith("eunpyeong/stations/") and path != "eunpyeong/stations/":
        s = subject  # 예: "녹번역"
        for label, href in _RL_THEMES:
            chips.append(_chip(f"{s} 인근 {label}", href))
        chips.append(_chip(f"{s} 예약 방법", "/reservation/"))
        chips.append(_chip(f"{s} 코스·요금", "/courses/#price"))
        chips.append(_chip("은평 지하철역별 안내 전체", "/eunpyeong/stations/"))
    elif path.startswith("eunpyeong/") and path not in ("eunpyeong/", "eunpyeong/stations/"):
        s = subject  # 예: "불광동"
        for label, href in _RL_THEMES:
            chips.append(_chip(f"{s} {label}", href))
        chips.append(_chip(f"{s} 방문 예약 안내", "/reservation/"))
        chips.append(_chip(f"{s} 코스·요금 보기", "/courses/#price"))
        chips.append(_chip(f"{s} 이용 후기", "/reviews/#area"))
    elif path.startswith("themes/") and path != "themes/":
        s = subject  # 예: "스웨디시"
        for label, href in _RL_AREAS:
            chips.append(_chip(f"{label} {s}", href))
        chips.append(_chip(f"{s} 코스·요금", "/courses/#price"))
        chips.append(_chip(f"{s} 예약 방법", "/reservation/"))
        chips.append(_chip(f"{s} 이용 후기", "/reviews/"))
        chips.append(_chip("전체 테마 안내", "/themes/"))
    elif path == "":
        # 메인 — 가장 많이 찾는 롱테일 조합을 한 곳에 모은다
        for label, href in [
            ("불광동 출장마사지", "/eunpyeong/bulgwang-dong/"),
            ("연신내 홈타이", "/eunpyeong/stations/yeonsinnae-station/"),
            ("응암동 24시간 마사지", "/eunpyeong/eungam-dong/"),
            ("은평뉴타운(진관동) 방문 관리", "/eunpyeong/jingwan-dong/"),
            ("녹번역 인근 마사지", "/eunpyeong/stations/nokbeon-station/"),
            ("커플 마사지 예약", "/themes/couple/"),
            ("심야 24시간 출장", "/themes/24hours/"),
            ("스웨디시 vs 타이마사지", "/magazine/swedish-vs-thai/"),
        ]:
            chips.append(_chip(label, href))
    else:
        return ""

    return (
        '<section class="related-links" aria-label="관련 안내">'
        '<h2>이런 주제도 함께 찾아보세요</h2>'
        f'<ul class="related-grid">{"".join(chips)}</ul>'
        '</section>'
    )


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 구조화 데이터(JSON-LD) — 페이지 종류별 일괄 생성
    schema_html = structured_data(page, path, canonical, noindex)

    # 내부 링크 강화 블록 — 본문 끝(요금/CTA 앞)에 삽입
    body = body + related_block(page, path)

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{verification_meta()}<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="{BRAND} 매거진" href="{BASE_URL.rstrip('/')}/rss.xml">
<link rel="sitemap" type="application/xml" href="{BASE_URL.rstrip('/')}/sitemap.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{schema_html}{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">간</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 은평구 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">은평구 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 은평구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">은평 출장마사지</a></li>
        <li><a href="/eunpyeong/">지역별 안내</a></li>
        <li><a href="/eunpyeong/stations/">지하철역별 안내</a></li>
        <li><a href="/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/magazine/">매거진</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def _sitemap_meta(path: str):
    """경로 성격에 따른 changefreq·priority 결정."""
    hubs = {"", "eunpyeong/", "eunpyeong/stations/", "themes/", "courses/",
            "magazine/", "massage/", "reservation/", "guide/", "reviews/", "support/"}
    if path == "":
        return "daily", "1.0"
    if path in hubs:
        return "weekly", "0.8"
    if path.startswith("magazine/"):
        return "monthly", "0.6"
    return "weekly", "0.7"


def _rfc822(date_str: str) -> str:
    """'YYYY-MM-DD' → RSS pubDate (KST 09:00 기준)."""
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return d.strftime("%a, %d %b %Y") + " 09:00:00 +0900"


def build() -> None:
    report = []
    sitemap_entries = []   # (url, lastmod, changefreq, priority)
    feed_items = []        # 매거진 RSS 아이템

    base = BASE_URL.rstrip("/")
    for page in PAGES:
        path = page["path"]  # "" 또는 "eunpyeong/bulgwang-dong/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        url = base + "/" + path
        lastmod = page.get("date", BUILD_DATE)
        if not noindex:
            changefreq, priority = _sitemap_meta(path)
            sitemap_entries.append((url, lastmod, changefreq, priority))
            # 매거진 글은 RSS 피드에도 싣는다 (허브 제외)
            if path.startswith("magazine/") and path != "magazine/" and page.get("date"):
                feed_items.append({
                    "title": page["title"].split(" | ")[0],
                    "url": url,
                    "desc": page["desc"],
                    "date": page["date"],
                })
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    # sitemap.xml (lastmod·changefreq·priority 포함)
    rows = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod>"
        f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        for u, lm, cf, pr in sitemap_entries
    )
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{rows}\n</urlset>\n"
        )

    # rss.xml (매거진 피드 — 네이버·구글 빠른 발견용)
    feed_items.sort(key=lambda x: x["date"], reverse=True)
    last_build = _rfc822(feed_items[0]["date"]) if feed_items else _rfc822(BUILD_DATE)
    items_xml = "\n".join(
        "    <item>"
        f"<title>{html.escape(it['title'])}</title>"
        f"<link>{it['url']}</link>"
        f"<guid isPermaLink=\"true\">{it['url']}</guid>"
        f"<description>{html.escape(it['desc'])}</description>"
        f"<pubDate>{_rfc822(it['date'])}</pubDate>"
        "</item>"
        for it in feed_items
    )
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "  <channel>\n"
            f"    <title>{html.escape(BRAND)} 매거진</title>\n"
            f"    <link>{base}/magazine/</link>\n"
            f'    <atom:link href="{base}/rss.xml" rel="self" type="application/rss+xml"/>\n'
            "    <description>은평 출장마사지·홈타이 이용 가이드와 관리 정보</description>\n"
            "    <language>ko</language>\n"
            f"    <lastBuildDate>{last_build}</lastBuildDate>\n"
            f"{items_xml}\n"
            "  </channel>\n</rss>\n"
        )

    # robots.txt (sitemap 위치 명시)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n"
        )

    # IndexNow 키 파일 — /<KEY>.txt 에 키 문자열만 담는다.
    if INDEXNOW_KEY:
        with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
            f.write(INDEXNOW_KEY + "\n")

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_entries)} in sitemap, "
          f"{len(feed_items)} in RSS feed.")


if __name__ == "__main__":
    build()
