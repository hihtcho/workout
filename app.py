import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장할 CSV 파일명
CSV_FILE = "workout_log.csv"

# 운동 카테고리 데이터
CATEGORY_DATA = {
    "어깨": ["전면 삼각근", "측면 삼각근", "후면 삼각근", "승모근"],
    "등": ["광배근", "승모근 중/하부", "척추기립근", "대원근"],
    "가슴": ["대흉근 상부", "대흉근 중부", "대흉근 하부", "전거근"],
    "코어": ["복직근", "외복사근", "복횡근"],
    "하체": ["대퇴사두근", "대퇴이두근(햄스트링)", "둔근(엉덩이)", "비복근(종아리)"],
    "팔": ["이두근", "삼두근", "전완근"]
}

# 기존 운동명 로드 함수
def load_existing_exercises():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            if '운동명' in df.columns:
                return df['운동명'].dropna().unique().tolist()
        except:
            pass
    return []

st.set_page_config(page_title="My Workout Note", layout="centered")
st.title("🏋️‍♂️ 운동 기록 노트")

# 1. 날짜 선택 (기본값: 오늘)
date = st.date_input("날짜를 선택하세요", datetime.today())

# 2. 대구분 선택
main_cat = st.selectbox("대구분 (부위)", list(CATEGORY_DATA.keys()))

# 3. 소구분 선택
sub_cat = st.selectbox("소구분 (근육)", CATEGORY_DATA[main_cat])

# 4. 운동명 입력/선택
existing_exercises = load_existing_exercises()
exercise_name = st.selectbox("기존 운동 선택 (직접 입력하려면 아래 칸 이용)", ["직접 입력"] + existing_exercises)

if exercise_name == "직접 입력":
    exercise_name = st.text_input("새로운 운동명 입력")

# 5. 수치 입력 (모바일용 가로 배치)
col1, col2, col3 = st.columns(3)
with col1:
    weight = st.number_input("무게 (kg)", min_value=0.0, step=0.5, format="%.1f")
with col2:
    reps = st.number_input("반복 횟수", min_value=0, step=1)
with col3:
    rest = st.number_input("휴식 (초)", min_value=0, step=5)

# 6. 비고 입력
memo = st.text_input("비고 (메모)")

# 7. 저장 버튼
if st.button("운동 기록 저장하기", use_container_width=True):
    if not exercise_name or exercise_name.strip() == "":
        st.error("운동명을 입력하거나 선택해주세요!")
    else:
        new_data = pd.DataFrame([{
            "날짜": date.strftime('%Y-%m-%d'),
            "대구분": main_cat,
            "소구분": sub_cat,
            "운동명": exercise_name.strip(),
            "무게(kg)": weight,
            "반복횟수": reps,
            "휴식시간(초)": rest,
            "비고": memo
        }])
        
        file_exists = os.path.exists(CSV_FILE)
        new_data.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
        st.success(f"🎉 [{exercise_name}] 기록이 저장되었습니다!")
        st.rerun()

# 저장된 데이터 미리보기 (선택사항)
if os.path.exists(CSV_FILE):
    st.write("---")
    st.subheader("📝 최근 운동 기록")
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    st.dataframe(df.tail(5), use_container_width=True)
