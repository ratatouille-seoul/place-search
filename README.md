# 📍 키워드 기반 장소 수집기 (카카오 API)

이 앱은 사용자가 입력한 장소명을 기준으로 반경 내 관련 장소들을 수집하고 엑셀로 저장합니다.

## 🖥 사용 방법
1. 이 저장소를 `Streamlit Cloud`로 배포하거나, 로컬에서 실행:
```bash
streamlit run place_search_gui_app.py
```

## ✅ 기능
- 카카오 API를 통한 키워드 장소 검색
- 장소명 입력 → 좌표 자동 변환
- 반경 지정 (미터 단위)
- 검색 결과 엑셀 저장

## 📦 필요 패키지
- streamlit
- pandas
- requests
- openpyxl

## 🛠 API KEY 설정
코드 내 `KAKAO_API_KEY = "여기에_본인_키"` 부분을 수정하세요.

---

© 2025 라따뚜이인서울
