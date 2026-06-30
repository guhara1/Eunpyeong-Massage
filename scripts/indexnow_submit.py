#!/usr/bin/env python3
"""IndexNow 즉시 색인 통보 스크립트.

IndexNow 한 번의 요청으로 참여 검색엔진(Bing, Naver, Yandex, Seznam 등)에
URL 변경을 즉시 알린다. Google은 IndexNow 미참여 — google_index.py 참고.

사용법:
  # 사이트맵의 모든 URL 통보 (글 다수 추가/전체 리프레시)
  python3 scripts/indexnow_submit.py --all

  # 특정 URL만 통보 (글 1~수개 올렸을 때 권장)
  python3 scripts/indexnow_submit.py https://eunpyeong-massage.netlify.app/magazine/new-post/

키 파일(/<KEY>.txt)이 도메인 루트에 배포되어 있어야 한다. build.py 가 자동 생성한다.
"""
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL, INDEXNOW_KEY  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sitemap_urls() -> list:
    tree = ET.parse(os.path.join(ROOT, "sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.findall(".//s:loc", ns)]


def submit(urls: list) -> None:
    if not INDEXNOW_KEY:
        sys.exit("INDEXNOW_KEY 가 content/site.py 에 설정되어 있지 않습니다.")
    if not urls:
        sys.exit("통보할 URL 이 없습니다.")
    host = BASE_URL.split("//", 1)[-1].strip("/")
    payload = {
        "host": host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE_URL.rstrip('/')}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"IndexNow 응답: HTTP {resp.status} — {len(urls)}개 URL 통보 완료")
    except urllib.error.HTTPError as e:
        # 200/202 외에도 키 검증 후 처리되는 경우가 있다.
        print(f"IndexNow 응답: HTTP {e.code} ({e.reason}) — {len(urls)}개 전송")
        body = e.read().decode("utf-8", "ignore").strip()
        if body:
            print("본문:", body)


def main() -> None:
    args = sys.argv[1:]
    if args == ["--all"]:
        urls = sitemap_urls()
    elif args and not args[0].startswith("-"):
        urls = args
    else:
        sys.exit(__doc__)
    print(f"전송 대상 {len(urls)}개:")
    for u in urls:
        print("  ", u)
    submit(urls)


if __name__ == "__main__":
    main()
