# 파이썬을 이용한 스타벅스 데이터 수집하기

파이썬을 이용하여 스타벅스 홈페이지에서 스타벅스 매장 정보를 수집하겠습니다.

## 폴더명

```
└── location [지역명, 지역 매장 갯수, 위도, 경도]
    ├── seoul
    ├── busan
    ├── daegu
    └── incheon
```

## 지역명

지역명은 다음과 같이 정리합니다.

```
location_name_mapping = {
    "서울": "seoul",
    "부산": "busan",
    "대구": "daegu",
    "인천": "incheon",
    "광주": "gwangju",
    "대전": "daejeon",
    "울산": "ulsan",
    "경기": "gyeonggi",
    "강원": "gangwon",
    "충북": "chungbuk",
    "충남": "chungnam",
    "전북": "jeolbuk",
    "전남": "jeolnam",
    "경북": "gyeongbuk",
    "경남": "gyeongnam",
    "제주": "jeju"
}

location_name_mapping = {
    "강남구": "gangnamgu",
    "강동구": "gangdonggu",
    "강북구": "gangbukgu",
    "강서구": "gangseogu",
    "관악구": "gwanakgu",
    "광진구": "gwangjingu",
    "구로구": "gurogu",
    "금천구": "geumcheongu",
    "노원구": "nowongu",
    "도봉구": "dobonggu",
    "동대문구": "dongdaemungu",
    "동작구": "dongjakgu",
    "마포구": "mapogu",
    "서대문구": "seodaemungu",
    "서초구": "seochogu",
    "성동구": "seongdonggu",
    "성북구": "seongbukgu",
    "송파구": "songpagu",
    "양천구": "yangcheongu",
    "영등포구": "yeongdeungpogu",
    "용산구": "yongsangu",
    "은평구": "eunpyeonggu",
    "종로구": "jongnogu",
    "중구": "junggu",
    "중랑구": "jungnanggu"
}
```
