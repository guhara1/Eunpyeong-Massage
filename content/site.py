# 사이트 공통 설정
BASE_URL = "https://eunpyeong-massage.pages.dev"

BRAND = "간다GO"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 검색엔진 소유확인 메타 (있을 때만 <head>에 출력)
NAVER_VERIFICATION = "a223edb54a8c0adb9484a5aedc3a1f3afab5533c"
GOOGLE_VERIFICATION = ""  # Google Search Console 확인 코드(있으면 입력)

# IndexNow 키 — 빌드 시 /<KEY>.txt 키 파일을 자동 생성한다.
# (IndexNow 참여: Bing, Naver, Yandex, Seznam 등)
INDEXNOW_KEY = "e1e3f963374737efc3bcccd03be66c08"

# 상단 메뉴 — 하위 메뉴에는 키워드를 반복하지 않고 지역명·역명만 표시한다.
NAV = [
    ("홈", "/", []),
    ("은평 출장마사지", "/massage/", [
        ("은평 출장마사지 안내", "/massage/#service"),
        ("은평 홈타이 안내", "/massage/#hometai"),
        ("은평구 전지역 방문 안내", "/massage/#coverage"),
        ("은평 지하철역 인근 안내", "/massage/#stations"),
        ("예약 가능 시간", "/massage/#hours"),
        ("코스 선택 안내", "/massage/#course"),
        ("이용 전 확인사항", "/massage/#check"),
        ("위생·안전 안내", "/massage/#safety"),
        ("자주 묻는 질문", "/massage/#faq"),
    ]),
    ("지역별 안내", "/eunpyeong/", [
        ("은평구 전체", "/eunpyeong/"),
        ("녹번동", "/eunpyeong/nokbeon-dong/"),
        ("불광동", "/eunpyeong/bulgwang-dong/"),
        ("갈현동", "/eunpyeong/galhyeon-dong/"),
        ("구산동", "/eunpyeong/gusan-dong/"),
        ("대조동", "/eunpyeong/daejo-dong/"),
        ("응암동", "/eunpyeong/eungam-dong/"),
        ("역촌동", "/eunpyeong/yeokchon-dong/"),
        ("신사동", "/eunpyeong/sinsa-dong/"),
        ("증산동", "/eunpyeong/jeungsan-dong/"),
        ("수색동", "/eunpyeong/susaek-dong/"),
        ("진관동", "/eunpyeong/jingwan-dong/"),
    ]),
    ("지하철역별 안내", "/eunpyeong/stations/", [
        ("역 전체", "/eunpyeong/stations/"),
        ("녹번역", "/eunpyeong/stations/nokbeon-station/"),
        ("불광역", "/eunpyeong/stations/bulgwang-station/"),
        ("연신내역", "/eunpyeong/stations/yeonsinnae-station/"),
        ("구파발역", "/eunpyeong/stations/gupabal-station/"),
        ("응암역", "/eunpyeong/stations/eungam-station/"),
        ("역촌역", "/eunpyeong/stations/yeokchon-station/"),
        ("독바위역", "/eunpyeong/stations/dokbawi-station/"),
        ("구산역", "/eunpyeong/stations/gusan-station/"),
        ("새절역", "/eunpyeong/stations/saejeol-station/"),
        ("증산역", "/eunpyeong/stations/jeungsan-station/"),
        ("수색역", "/eunpyeong/stations/susaek-station/"),
        ("디지털미디어시티역", "/eunpyeong/stations/digital-media-city-station/"),
    ]),
    ("테마별 안내", "/themes/", [
        ("전체 테마", "/themes/"),
        ("스웨디시", "/themes/swedish/"),
        ("로미로미", "/themes/lomilomi/"),
        ("타이마사지", "/themes/thai/"),
        ("중국마사지", "/themes/chinese/"),
        ("아로마테라피", "/themes/aroma/"),
        ("홈케어", "/themes/homecare/"),
        ("호텔식마사지", "/themes/hotel-style/"),
        ("발마사지", "/themes/foot/"),
        ("스포츠·경락", "/themes/sports/"),
        ("스킨케어", "/themes/skincare/"),
        ("왁싱", "/themes/waxing/"),
        ("커플 관리", "/themes/couple/"),
        ("24시간", "/themes/24hours/"),
        ("수면 가능", "/themes/overnight/"),
    ]),
    ("코스안내", "/courses/", [
        ("전체 코스", "/courses/"),
        ("피로 회복 관리", "/courses/#recovery"),
        ("아로마 관리", "/courses/#aroma"),
        ("스포츠 관리", "/courses/#sports"),
        ("홈타이 코스", "/courses/#hometai"),
        ("커플·가족 방문 관리", "/courses/#couple"),
        ("기업·단체 방문 관리", "/courses/#group"),
        ("가격 안내", "/courses/#price"),
        ("코스 선택 가이드", "/courses/#guide"),
    ]),
    ("예약안내", "/reservation/", [
        ("예약 방법", "/reservation/#how"),
        ("예약 가능 시간", "/reservation/#hours"),
        ("방문 가능 장소", "/reservation/#place"),
        ("결제 안내", "/reservation/#payment"),
        ("변경·취소 안내", "/reservation/#change"),
        ("예약 전 체크사항", "/reservation/#check"),
    ]),
    ("이용가이드", "/guide/", [
        ("처음 이용하시는 분", "/guide/#first"),
        ("방문 전 준비사항", "/guide/#prepare"),
        ("위생 및 안전 기준", "/guide/#hygiene"),
        ("관리 후 주의사항", "/guide/#after"),
        ("금지행위 안내", "/guide/#prohibited"),
        ("이용 FAQ", "/guide/#faq"),
    ]),
    ("후기", "/reviews/", [
        ("전체 후기", "/reviews/"),
        ("지역별 후기", "/reviews/#area"),
        ("역세권 후기", "/reviews/#station"),
        ("후기 작성 안내", "/reviews/#write"),
    ]),
    ("고객센터", "/support/", [
        ("공지사항", "/support/#notice"),
        ("자주 묻는 질문", "/support/#faq"),
        ("1:1 문의", "/support/#contact"),
        ("제휴·기업 문의", "/support/#biz"),
        ("개인정보처리방침", "/support/privacy/"),
        ("이용약관", "/support/terms/"),
    ]),
]
