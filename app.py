# 💡 7. 저장 버튼 및 방금 기록 삭제(취소) 버튼 (나란히 배치)
save_col, del_col = st.columns([0.75, 0.25]) # 저장 버튼을 크게, 삭제 버튼을 작게 배정

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
    # popover를 사용하여 버튼 클릭 시에만 입력창이 나타나도록 구현
    with st.popover("↩️ 직전 기록 취소", use_container_width=True):
        st.write("방금 저장한 마지막 1줄을 삭제합니다.")
        pw = st.text_input("비밀번호 입력", type="password", key="delete_pw")
        if st.button("삭제 확인", use_container_width=True):
            if pw == "1234":
                if os.path.exists(CSV_FILE):
                    try:
                        df = pd.read_csv(CSV_FILE, encoding='utf-8-sig')
                        if not df.empty:
                            # 💡 맨 마지막 줄(직전 기록)만 제외하고 다시 저장
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
