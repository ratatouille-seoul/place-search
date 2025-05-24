# -*- coding: utf-8 -*-
import streamlit as st
import requests
import pandas as pd
import time
from urllib.parse import quote
from datetime import datetime
import re

# === 사용자 설정 ===
KAKAO_API_KEY = '9413618fb8b362446e851b5ddd0e990c'

# === 좌표 조회 함수 ===
def get_coordinates(place_name):
    query = quote(place_name)
    url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "Accept-Charset": "utf-8"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        st.error(f"[좌표 오류] 요청 실패: {res.status_code}")
        return None, None
    documents = res.json().get("documents", [])
    if not documents:
        return None, None
    return float(documents[0]['x']), float(documents[0]['y'])

# === 지번주소 조회 함수 ===
def get_jibun_address(x, y):
    url = f"https://dapi.kakao.com/v2/local/geo/coord2address.json?x={x}&y={y}"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return ""
    result = res.json()
    try:
        return result['documents'][0]['address']['address_name']
    except (KeyError, IndexError):
        return ""

# === 주소 구성 요소 추출 함수 ===
def extract_address_parts(road_address, jibun_address):
    si = gu = dong = eup = myeon = ri = road = ""

    # 시/도, 구/군
    match1 = re.search(r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[\s]*([\w가-힣]+구|[\w가-힣]+군)?', road_address)
    if match1:
        si = match1.group(1) or ""
        gu = match1.group(2) or ""

    # 동/읍/면/리 (지번주소에서 보완)
    match2 = re.search(r'([\w가-힣]+(동|읍|면|리))', jibun_address)
    if match2:
        if '동' in match2.group(1):
            dong = match2.group(1)
        elif '읍' in match2.group(1):
            eup = match2.group(1)
        elif '면' in match2.group(1):
            myeon = match2.group(1)
        elif '리' in match2.group(1):
            ri = match2.group(1)

    # 도로명
    match3 = re.search(r'([\w가-힣\d]+로)', road_address)
    if match3:
        road = match3.group(1)

    return si, gu, dong, eup, myeon, ri, road

# === 장소 검색 함수 ===
def search_places(x, y, radius, keywords):
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "Accept-Charset": "utf-8"
    }
    all_places = []
    for keyword in keywords:
        query = quote(keyword)
        page = 1
        st.write(f"🔍 검색 중: {keyword}")
        while True:
            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&x={x}&y={y}&radius={radius}&page={page}&size=15"
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                st.error(f"[요청 실패] 상태코드 {res.status_code}")
                st.text(res.text)
                break
            data = res.json()
            documents = data.get("documents", [])
            if not documents:
                break
            for item in documents:
                jibun_address = get_jibun_address(item['x'], item['y'])
                si, gu, dong, eup, myeon, ri, road = extract_address_parts(item['road_address_name'], jibun_address)
                all_places.append({
                    '검색어': keyword,
                    '시': si,
                    '구': gu,
                    '동': dong,
                    '읍': eup,
                    '면': myeon,
                    '리': ri,
                    '도로명': road,
                    '장소명': item['place_name'],
                    '주소': item['road_address_name'],
                    '위도': item['y'],
                    '경도': item['x']
                })
            if data['meta'].get('is_end'):
                break
            page += 1
            time.sleep(0.3)
    return all_places

# === Streamlit 인터페이스 ===
st.title("📍 키워드 기반 장소 수집기 (카카오 API)")
place_name = st.text_input("장소명을 입력하세요 (예: 강남역)", "라따뚜이인서울")
radius = st.number_input("반경 설정 (미터 단위)", min_value=100, max_value=20000, value=1000, step=100)

if st.button("검색 시작"):
    x, y = get_coordinates(place_name)
    if x is None or y is None:
        st.error("❌ 장소를 찾을 수 없습니다. 정확히 입력해주세요.")
    else:
        keywords = [
    "가", "강", "건", "경", "계", "고", "곡", "공", "관", "광", "교", "구", "국", "군", "금", "기",
    "길", "나", "낙", "남", "내", "노", "누", "다", "단", "당", "대", "덕", "도", "동", "두", "등",
    "라", "로", "리", "마", "만", "명", "모", "무", "문", "미", "민", "박", "반", "방", "배", "백",
    "범", "법", "복", "봉", "부", "북", "분", "불", "사", "산", "삼", "상", "서", "석", "선", "설",
    "성", "세", "소", "송", "수", "숙", "순", "시", "신", "심", "아", "안", "양", "어", "엄", "여",
    "역", "연", "열", "영", "오", "온", "와", "왕", "용", "우", "운", "울", "원", "월", "위", "유",
    "윤", "은", "읍", "응", "의", "이", "인", "일", "임", "자", "장", "전", "정", "제", "조", "주",
    "죽", "중", "지", "진", "창", "천", "철", "청", "초", "춘", "충", "치", "친", "타", "탑", "통",
    "파", "평", "포", "하", "한", "함", "해", "현", "형", "호", "홍", "화", "효", "흥",
    "강당", "강의실", "거리", "검찰청", "게스트하우스", "결혼식장", "경찰서", "계곡", "고객센터", "고등법원",
    "고등학교", "고속터미널", "공공시설", "공단", "공연장", "공영", "공영주차장", "공원", "공장", "과학관",
    "광역시청", "광역환승", "광장", "교육청", "구립", "구청", "국공립", "국립병원", "국민체육센터", "국악당",
    "군청", "기념관", "기업지원센터", "노인복지관", "노인센터", "노인정", "놀이터", "다세대", "단독주택",
    "도서관", "도청", "동물원", "동사무소", "디지털도서관", "레지던스", "리조트", "마을회관", "마트", "모텔",
    "문화관", "문화센터", "문화예술회관", "문화원", "문화의집", "문화회관", "미술관", "민박", "박람회",
    "박람회장", "박물관", "방송국", "백화점", "법원청사", "별관", "병원", "보건소", "보훈병원", "복지관",
    "복합단지", "복합센터", "본관", "분관", "분소", "빌딩", "빌라", "사회복지관", "상가", "생태원",
    "생활체육관", "센터", "소방서", "수목원", "수족관", "시립", "시민회관", "시설", "시의회", "시장",
    "시청", "식물원", "신문사", "아트센터", "아파트", "약국", "어린이집", "여관", "여성회관", "여인숙",
    "역", "역사박물관", "연구소", "연립", "연수원", "영업소", "예술의전당", "예술회관", "예식장", "오피스텔",
    "우체국", "운동장", "유치원", "음악당", "의원", "전당", "전망대", "전시관", "전시센터", "전시장",
    "전시홀", "전통시장", "정류장", "정보관", "정보도서관", "정보센터", "정원", "종합복지관", "주거복합",
    "주민센터", "주상복합", "주차장", "주택", "중앙역", "중학교", "지구대", "지방경찰청", "지방법원", "지사",
    "지원청", "지점", "지하철", "창고", "창업보육센터", "창업지원센터", "천문대", "청소년문화의집",
    "청소년센터", "청소년수련관", "체육관", "체험관", "체험장", "초등학교", "출입구", "컨벤션센터", "콘도",
    "타워", "터미널", "파출소", "펜션", "편의점", "플라자", "하우스", "학교", "학생회관", "학원", "해양관",
    "현대미술관", "호스텔", "호텔", "환승", "환승센터", "회관", "과학관", "광장",
    "공항", "지하철", "호선", "정류장", "버스", "스퀘어", "타운", "문화", "전철", "입구", "정문", "후문", "중문", "출구",
    "공공", "공용", "기관", "협회", "단체", "캠퍼스", "본부", "학사", "생활관", "도서관", "연구실", "강의동",
    "사당", "서원", "사찰", "성당", "성지", "유적", "사적지", "문화재", "탑", "불상",
    "항", "부두", "출입문", "방면", "전철역", "역세권",
    "문화마을", "벽화마을", "돌담길", "골목길", "회랑", "루트"
     ]
        result = search_places(x, y, radius, keywords)
        if result:
            df = pd.DataFrame(result)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"장소_반경1km_키워드결과_{now}.xlsx"
            df.to_excel(filename, index=False)
            st.success(f"✅ 저장 완료: {filename} (총 {len(result)}개)")
            st.dataframe(df)
        else:
            st.warning("⚠️ 결과가 없습니다.")
