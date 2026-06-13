#!/usr/bin/env python3
"""Google Indexing API 색인 요청 스크립트 (선택).

주의: Google Indexing API 는 공식적으로 JobPosting·BroadcastEvent 구조화
데이터 페이지를 위한 것이다. 일반 콘텐츠 페이지에도 호출은 되지만 색인이
보장되지는 않는다. 일반 페이지의 가장 확실한 경로는 Search Console 사이트맵
제출 + 'URL 검사 → 색인 요청' 이다. 이 스크립트는 보조 수단이다.

사전 준비:
  1) Google Cloud 프로젝트에서 Indexing API 활성화
  2) 서비스 계정 생성 → JSON 키 발급
  3) Search Console 자산에 그 서비스 계정 이메일을 '소유자'로 추가
  4) pip install google-auth requests

사용법:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json
  python3 scripts/google_index.py https://eunpyeong-massage.pages.dev/magazine/new-post/
  python3 scripts/google_index.py --all     # 사이트맵 전체
"""
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"


def sitemap_urls() -> list:
    tree = ET.parse(os.path.join(ROOT, "sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.findall(".//s:loc", ns)]


def main() -> None:
    args = sys.argv[1:]
    if args == ["--all"]:
        urls = sitemap_urls()
    elif args and not args[0].startswith("-"):
        urls = args
    else:
        sys.exit(__doc__)

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")

    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("pip install google-auth requests 를 먼저 실행하세요.")

    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)

    ok = 0
    for url in urls:
        r = session.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"})
        status = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
        print(f"  [{status}] {url}")
        if r.status_code != 200:
            print("    ", r.text.strip()[:300])
        else:
            ok += 1
    print(f"\n{ok}/{len(urls)} 건 색인 요청 완료.")


if __name__ == "__main__":
    main()
