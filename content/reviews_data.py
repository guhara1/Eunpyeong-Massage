# 이용 후기 데이터 — 후기 페이지의 화면 표시와 Review/AggregateRating 구조화 데이터에 함께 사용한다.
# 표시되는 후기와 스키마가 1:1로 일치해야 검색엔진 정책에 부합한다(보이지 않는 별점 금지).
# (name: 일부만 표기 / area: 대표 동 / theme·theme_href: 테마 연결 / rating: 1~5 / date: YYYY-MM-DD)

REVIEWS = [
    {"name": "김O은", "area": "불광동", "theme": "스웨디시", "theme_href": "/themes/swedish/",
     "rating": 5, "date": "2026-06-21",
     "text": "연신내 쪽 오피스텔인데 예약 전화부터 친절했고 말씀하신 시간에 정확히 도착하셨어요. 압도 중간중간 물어봐 주셔서 딱 맞게 받았습니다. 받고 나서 그날 밤 정말 푹 잤어요."},
    {"name": "이O호", "area": "응암동", "theme": "타이마사지", "theme_href": "/themes/thai/",
     "rating": 5, "date": "2026-06-18",
     "text": "홈타이 처음 받아봤는데 오일 안 쓰니까 샤워 부담 없어서 평일 저녁에 받기 딱 좋네요. 굳은 어깨랑 종아리 스트레칭 시원하게 풀렸습니다. 다음에 또 부를게요."},
    {"name": "박O정", "area": "진관동", "theme": "아로마테라피", "theme_href": "/themes/aroma/",
     "rating": 5, "date": "2026-06-15",
     "text": "은평뉴타운 신축인데 방문 차량 등록 안내까지 미리 챙겨주셔서 헤매지 않았어요. 향이 은은하고 90분이 금방 갔습니다. 부모님 선물로도 예약하려고요."},
    {"name": "최O아", "area": "녹번동", "theme": "스포츠·경락", "theme_href": "/themes/sports/",
     "rating": 4, "date": "2026-06-12",
     "text": "백련산 등산 후 다리가 너무 뭉쳐서 불렀어요. 부위 집중해서 잘 풀어주셨습니다. 도착이 10분 정도 늦었는데 미리 연락 주셔서 괜찮았어요."},
    {"name": "정O욱", "area": "역촌동", "theme": "타이마사지", "theme_href": "/themes/thai/",
     "rating": 5, "date": "2026-06-09",
     "text": "야근 끝나고 밤 11시에 받았는데 시간대 상관없이 응대가 한결같았어요. 조용히 진행해 주셔서 옆방 가족 안 깨우고 잘 받았습니다."},
    {"name": "한O림", "area": "구산동", "theme": "커플 관리", "theme_href": "/themes/couple/",
     "rating": 5, "date": "2026-06-05",
     "text": "결혼기념일에 둘이 같이 받았어요. 관리사분 두 분이 동시에 진행해 주셔서 분위기 좋게 받았습니다. 각자 다른 테마 골라도 된다고 해서 만족도 높았어요."},
    {"name": "오O서", "area": "대조동", "theme": "아로마테라피", "theme_href": "/themes/aroma/",
     "rating": 5, "date": "2026-06-01",
     "text": "연신내 로데오 근처 집인데 주차 위치까지 친절히 물어봐 주셨어요. 향이 좋아서 받는 내내 편안했고 끝나고 정리도 깔끔하게 해주셨습니다."},
    {"name": "서O민", "area": "신사동", "theme": "발마사지", "theme_href": "/themes/foot/",
     "rating": 4, "date": "2026-05-27",
     "text": "하루 종일 서서 일해서 발이 퉁퉁 부었는데 발마사지 받고 한결 가벼워졌어요. 다음엔 전신 90분으로 받아보려고요."},
    {"name": "윤O경", "area": "증산동", "theme": "스웨디시", "theme_href": "/themes/swedish/",
     "rating": 5, "date": "2026-05-23",
     "text": "DMC 직장인데 퇴근하고 집에서 바로 받으니 이동이 없어 너무 편해요. 압 조절을 잘해주셔서 자다 깬 듯 개운하게 마무리했습니다."},
    {"name": "강O준", "area": "갈현동", "theme": "홈케어", "theme_href": "/themes/homecare/",
     "rating": 5, "date": "2026-05-19",
     "text": "어머니 모시고 사는데 어르신 가벼운 관리로 부탁드렸더니 무리 없이 부드럽게 진행해 주셨어요. 어머니가 다음에 또 받고 싶다고 하시네요."},
    {"name": "임O아", "area": "수색동", "theme": "타이마사지", "theme_href": "/themes/thai/",
     "rating": 5, "date": "2026-05-14",
     "text": "수색역 근처 숙소에서 출장으로 받았는데 숙소 출입 안내드리니 정확하게 찾아오셨어요. 출장 다니며 쌓인 피로가 확 풀렸습니다."},
    {"name": "조O빈", "area": "불광동", "theme": "스포츠·경락", "theme_href": "/themes/sports/",
     "rating": 4, "date": "2026-05-08",
     "text": "헬스 후 회복 목적으로 받았어요. 종목이랑 불편한 부위 먼저 물어보고 시간 배분해 주셔서 좋았습니다. 예약이 몰리는 주말은 미리 잡는 게 좋아요."},
]

# 표시 후기 기반 집계(별점 평균·후기 수). 화면·스키마가 동일 데이터를 쓰므로 항상 일치한다.
REVIEW_COUNT = len(REVIEWS)
_avg = sum(r["rating"] for r in REVIEWS) / REVIEW_COUNT
RATING_VALUE = f"{_avg:.1f}"          # 예: "4.8"
RATING_BEST = "5"
RATING_WORST = "1"
