# 색인(인덱싱) 운영 가이드 — 간다GO 은평 출장마사지

도메인: **https://eunpyeong-massage.netlify.app** (Netlify)

빌드(`python3 build.py`)가 자동 생성하는 색인 관련 파일:

| 파일 | 용도 |
|---|---|
| `sitemap.xml` | 색인 가능한 55개 URL + `lastmod`·`changefreq`·`priority` |
| `rss.xml` | 매거진 글 RSS 2.0 피드 (네이버·구글 빠른 발견용) |
| `robots.txt` | 전체 허용 + 사이트맵 위치 |
| `<INDEXNOW_KEY>.txt` | IndexNow 키 파일 (도메인 루트 배포) |
| 모든 페이지 `<head>` | 네이버 소유확인 메타, RSS·사이트맵 link 태그 |

> 본문 2,000자 미만 페이지(약관·개인정보)는 자동 `noindex` 처리되어 사이트맵·RSS에서 제외됩니다.

---

## 1. 네이버 — 가장 빠른 색인

홈페이지에 이미 소유확인 메타가 들어가 있습니다:
`<meta name="naver-site-verification" content="d4924fbe8147322f13531043507ecae74e46e27b">`

1. [네이버 서치어드바이저](https://searchadvisor.naver.com) → 사이트 등록 → `https://eunpyeong-massage.netlify.app`
2. **소유확인**: HTML 태그 방식 선택(메타 이미 적용됨) → 확인
3. **요청 → 사이트맵 제출**: `https://eunpyeong-massage.netlify.app/sitemap.xml`
4. **요청 → RSS 제출**: `https://eunpyeong-massage.netlify.app/rss.xml`
5. **요청 → 웹페이지 수집**: 메인·주요 페이지 URL을 직접 넣어 수집 요청
6. 네이버는 **IndexNow 참여사**이므로 아래 4번 스크립트로도 즉시 통보됩니다.

---

## 2. 구글 — Search Console

1. [Search Console](https://search.google.com/search-console) → 속성 추가 → URL 접두어 `https://eunpyeong-massage.netlify.app`
2. 소유확인: **HTML 태그** 방식이 가장 간단합니다.
   - 발급받은 코드를 `content/site.py` 의 `GOOGLE_VERIFICATION = "..."` 에 입력 → `python3 build.py` → 배포 → 확인
   - (또는 Cloudflare DNS TXT 방식)
3. **Sitemaps** 메뉴 → `sitemap.xml` 제출
4. **URL 검사** → 핵심 페이지(메인, 지역·역 허브, 신규 글) → **색인 생성 요청**
5. 구글은 IndexNow 미참여 → 더 빠르게 밀어넣고 싶으면 5번(Indexing API).

---

## 3. RSS 피드

`rss.xml` 은 매거진 글을 최신순으로 싣습니다. 네이버 서치어드바이저 RSS 제출,
그리고 피드 수집기/디스커버 계열 발견에 도움이 됩니다. 새 글을 올리면 빌드 시
자동 갱신됩니다.

---

## 4. IndexNow — 글 올릴 때마다 즉시 통보 (Bing·네이버·얀덱스)

키 파일 `e1e3f963374737efc3bcccd03be66c08.txt` 가 도메인 루트에 배포돼 있어야 합니다
(빌드가 자동 생성). 글 추가/수정 후 배포가 끝나면:

```bash
# 새 글 1~수개만 통보 (권장)
python3 scripts/indexnow_submit.py https://eunpyeong-massage.netlify.app/magazine/new-post/

# 사이트맵 전체 통보 (대규모 갱신 시)
python3 scripts/indexnow_submit.py --all
```

한 번 호출로 IndexNow 참여 검색엔진 전체에 전파됩니다. 별도 라이브러리 불필요(표준 라이브러리).

---

## 5. 구글 Indexing API (선택)

구글 Indexing API 는 공식적으로 JobPosting·BroadcastEvent 용이라 일반 페이지
색인을 **보장하지 않습니다**. 일반 페이지는 4·1·2번이 정석이며, 이건 보조 수단입니다.

```bash
pip install google-auth requests
export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json
python3 scripts/google_index.py https://eunpyeong-massage.netlify.app/magazine/new-post/
```

사전: Cloud 프로젝트에서 Indexing API 활성화 → 서비스 계정 JSON 발급 →
Search Console 속성에 서비스 계정 이메일을 **소유자**로 추가.

---

## 6. sitemap ping 자동화에 대하여 (중요)

`google.com/ping?sitemap=` 핑은 **2023년 6월 구글이 폐지**했고, Bing도 핑 대신
IndexNow 를 권장하며 사실상 폐지했습니다. 즉 옛날식 사이트맵 핑은 더 이상
동작하지 않습니다. **현재의 정답은 IndexNow(4번) + Search Console 사이트맵 제출(1·2번)**
이며, 본 저장소는 그 방식으로 구성돼 있습니다.

---

## 새 글 발행 체크리스트

1. `content/magazine.py` 에 글 추가 (`_post(...)`, 날짜 포함) → `PAGES` 에 등록
2. `python3 build.py` → sitemap·rss·페이지 자동 갱신
3. 커밋 & 푸시 → Netlify 자동 배포
4. `python3 scripts/indexnow_submit.py <새 글 URL>` 실행 (네이버·Bing 즉시 통보)
5. (구글) Search Console URL 검사 → 색인 생성 요청
