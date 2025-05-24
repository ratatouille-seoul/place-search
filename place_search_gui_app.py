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

# === 함수 정의 ===
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
        st.text(res.text)
        return None, None
    documents = res.json().get("documents", [])
    if not documents:
        return None, None
    return float(documents[0]['x']), float(documents[0]['y'])

def extract_address_parts(road_address):
    si = gu = dong = eup = myeon = ri = road = ""
    # 시/도, 구/군
    match1 = re.search(r'(서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)[\s]*([\w가-힣]+구|[\w가-힣]+군)?', road_address)
    if match1:
        si = match1.group(1) or ""
        gu = match1.group(2) or ""

    # 동/읍/면/리
    match2 = re.search(r'(\w+[동읍면리])', road_address)
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
                si, gu, dong, eup, myeon, ri, road = extract_address_parts(item['road_address_name'])
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
        keywords = ["가", "강", "건", "경", "계"]  # 생략: 원래 키워드 목록 유지
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
