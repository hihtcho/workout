import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 데이터 저장할 CSV 파일명
CSV_FILE = "workout_log.csv"

# 운동 카테고리 데이터
CATEGORY_DATA = {
    "유산소": ["경사 워킹", "타바타", "캐틀벨 스윙", "인터발 러닝"],
    "어깨": ["전면 삼각근", "측면 삼각근", "후면 삼각근", "승모근"],
    "등": ["광배근", "승모근 중/하부", "척추기립근", "대원근"],
    "가슴": ["대흉근 상부", "대흉근 중부", "대흉근 하부", "전거근"],
    "코어": ["복직근", "외복사근", "복횡근"],
    "하체": ["대퇴사두근", "대퇴이두근(햄스트링)", "둔근(엉덩이)", "비복근(종아리)"],
    "팔": ["이두근", "삼두근", "전완근"]
}

# 현재 선택된 소구분에 맞는 기존 운동명만 로드하는 함수
def load_existing_exercises_by_subcat(sub_cat_name):
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            if '소구분' in df.columns and '운동명' in df.columns:
                df_filtered = df[df['소구분'] == sub_cat_name.strip()]
                return df_filtered['운동명'].dropna().unique().tolist()
        except:
            pass
    return []

# 특정 운동의 가장 최근 기록(무게, 반복, 휴식)을 가져오는 함수
def load_last_workout_values(exercise_name):
    default_values = {"무게(kg)": 0.0, "반복횟수": 0, "휴식시간(초)": 0}
    if not exercise_name or exercise_name == "직접 입력":
        return default_values
        
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            df_filtered = df[df['운동명'] == exercise_name.strip()]
            if not df_filtered.empty:
                last_row = df_filtered.iloc[-1]
                return {
                    "무게(kg)": float(last_row.get('무게(kg)', 0.0)),
                    "반복횟수": int(last_row.get('반복횟수', 0)),
                    "휴식시간(초)": int(last_row.get('휴식시간(초)', 0))
                }
        except:
            pass
    return default_values

# 💡 오늘 자 해당 운동의 다음 세트 수를 자동으로 계산하는 함수
def get_next_set_number(date_str, exercise_name):
    if not exercise_name or exercise_name == "직접 입력":
        return 1
        
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
            if '날짜' in df.columns and '운동명' in df.columns:
                # 오늘 날짜에 저장된 동일 운동 필터링
                same_day_workout = df[(df['날짜'] == date_str) & (df['운동명'] == exercise_name.strip())]
                if not same_day_workout.empty:
                    if '세트' in same_day_workout.columns:
                        return int(same_day_workout['세트'].max()) + 1
                    else:
                        return len(same_day_workout) + 1
        except:
            pass
    return 1

st.set_page_config(page_title="My Workout Note", layout="centered")
st.title("🏋️‍♂️ 운동 기록 노트")

# 1. 날짜 선택
date = st.date_input("날짜를 선택하세요", datetime.today())
date_str = date.strftime('%Y-%m-%d')

# 2 & 3. 대구분과 소구분 (가로 정렬)
cat_col1, cat_col2 = st.columns(2)
with cat_col1:
    main_cat = st.selectbox("대구분 (부위)", list(CATEGORY_DATA.keys()))
with cat_col2:
    sub_cat = st.selectbox("소구분 (근육)", CATEGORY_DATA[main_cat])

# 4. 운동명 입력/선택
existing_exercises = load_existing_exercises_by_subcat(sub_cat)
selected_exercise = st.selectbox("기존 운동 선택", ["직접 입력"] + existing_exercises)

exercise_name = ""
if selected_exercise == "직접 입력":
    exercise_name = st.text_input("새로운 운동명 입력")
else:
    exercise_name = selected_exercise

# 직전 기록(무게, 반복, 휴식) 불러오기
last_values = load_last_workout_values(exercise_name)

# 💡 오늘 기록할 세트 수 계산 (오늘 한 적 없으면 1, 있으면 마지막 세트 + 1)
next_set_value = get_next_set_number(date_str, exercise_name)

# 5. 수치 입력 (4열 배치: 무게 -> 반복 -> 세트 -> 휴식)
col1, col2, col3, col4 = st.columns(4)
with col1:
    weight = st.number_input("무게 (kg)", min_value=0.0, step=0.5, format="%.1f", value=last_values["무게(kg)"])
with col2:
    reps = st.number_input("반복 횟수", min_value=0, step=1, value=last_values["반복횟수"])
with col3:
    # 💡 자동 계산된 다음 세트 수가 세팅되며, 수동 조절도 가능합니다.
    set_num = st.number_input("세트 수", min_value=1, step=1, value=next_set_value)
with col4:
    rest = st.number_input("휴식 (초)", min_value=0, step=5, value=last_values["휴식시간(초)"])

# 6. 비고 입력
memo = st.text_input("비고 (메모)")

# 7. 저장 버튼 및 방금 기록 삭제(취소) 버튼 (나란히 배치)
save_col, del_col = st.columns([0.75, 0.25])

with save_col:
    if st.button("운동 기록 저장하기", use_container_width=True, type="primary"):
        if not exercise_name or exercise_name.strip() == "":
            st.error("운동명을 입력해주세요!")
        else:
            new_data = pd.DataFrame([{
                "날짜": date_str, "대구분": main_cat, "소구분": sub_cat,
                "운동명": exercise_name.strip(), "세트": set_num,
                "무게(kg)": weight, "반복횟수": reps, "휴식시간(초)": rest, "비고": memo
            }])
            file_exists = os.path.exists(CSV_FILE)
            new_data.to_csv(CSV_FILE, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            st.success(f"🎉 {exercise_name} 저장 완료!")
            st.rerun()

with del_col:
    with st.popover("↩️ 직전 기록 취소", use_container_width=True):
        st.write("방금 저장한 마지막 1줄을 삭제합니다.")
        pw = st.text_input("비밀번호 입력", type="password", key="delete_pw")
        if st.button("삭제 확인", use_container_width=True):
            if pw == "1234":
                if os.path.exists(CSV_FILE):
                    try:
                        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
                        if not df.empty:
                            df_dropped = df.drop(df.index[-1])
                            df_dropped.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
                            st.success("방금 입력한 기록이 취소되었습니다.")
                            st.rerun()
                        else:
                            st.info("삭제할 기록이 없습니다.")
                    except Exception as e:
                        st.error(f"파일을 수정하는 중 오류 발생: {e}")
                else:
                    st.info("데이터 파일이 없습니다.")
            else:
                st.error("비밀번호 불일치")

# 저장된 데이터 미리보기
if os.path.exists(CSV_FILE):
    st.write("---")
    st.subheader("📝 최근 운동 기록")
    df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
    st.dataframe(df.tail(5), use_container_width=True)
