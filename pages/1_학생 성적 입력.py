import streamlit as st
from pymongo import MongoClient
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# MongoDB 연결 설정
MONGO_URI = "mongodb+srv://jsheek93:j103203j@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

user_db = client["user_database"]
student_collection = user_db["student"]

highschool_db = client["highschool_db"]
classes_info_collection = highschool_db["classes_info"]

teacher_db = client["teacher_page"]
evaluation_collection = teacher_db["evaluation"]

def main():
    st.title("학생 성적 입력")
    student_id = st.text_input("평가할 학생의 학번을 입력해주세요❣", key="student_id")

    if student_id:
        # 학생 학번으로 학생 정보 조회
        student = student_collection.find_one({"학번": student_id})
        if student:
            st.write(f"학생 이름: {student['이름']}")
            # 학생이 선택할 수 있는 과목 리스트 제공
            subjects = classes_info_collection.distinct("subject_name")
            selected_subject = st.selectbox("과목 선택", subjects, key="selected_subject")

            if selected_subject:
                # 선택된 과목의 수업 리스트 제공
                classes = classes_info_collection.find_one({"subject_name": selected_subject})["classes"]
                class_names = [cls["class_name"] for cls in classes]
                selected_class = st.selectbox("수업 선택", class_names, key="selected_class")

                # 선택된 수업의 상세 정보 출력
                if selected_class:
                    class_info = next(cls for cls in classes if cls["class_name"] == selected_class)
                    
                    # 성취 목표 출력 및 채점 (2열의 테이블로 구성)
                    achievements_str = class_info.get("achievements", "")
                    achievements_list = achievements_str.split('"')[1::2]
                    st.write("성취 목표:")

                    data = []
                    for achievement in achievements_list:
                        data.append({"성취 목표": achievement.strip(), "성적 등급": ""})

                    # 데이터프레임 생성
                    df = pd.DataFrame(data)

                    # AgGrid 설정
                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_default_column(editable=True, resizable=True)
                    gb.configure_column("성적 등급", editable=True, cellEditor='agSelectCellEditor', cellEditorParams={"values": ["A", "B", "C"]})
                    gb.configure_grid_options(domLayout='normal')
                    grid_options = gb.build()

                    # 테이블 출력 및 수정 가능하도록 설정 (표 크기 확장)
                    grid_response = AgGrid(
                        df,
                        gridOptions=grid_options,
                        update_mode='value_changed',
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                        editable=True,
                        height=200,
                        width=2000, 
                        fit_columns_on_grid_load=False
                    )

                    # 수정된 데이터 가져오기
                    updated_data = grid_response['data']
                    st.write("---")

                    # 교사가 성적등급 및 피드백 입력
                    overall_grade = st.selectbox("전체 성적등급 입력", ["A", "B", "C", "D", "E", "F"], key="overall_grade")
                    feedback = st.text_area("피드백 입력", key="feedback")
                    if st.button("피드백 저장", key="save_feedback"):
                        if feedback and overall_grade:
                            evaluation_data = {
                                "학번": student_id,
                                "이름": student["이름"],
                                "수강과목": selected_subject,
                                "수강강좌": selected_class,
                                "성취목표채점": updated_data.to_dict(orient="records"),
                                "성적등급": overall_grade,
                                "피드백": feedback
                            }
                            evaluation_collection.insert_one(evaluation_data)
                            st.success("피드백과 성적등급이 저장되었습니다.")
                        else:
                            st.error("성적등급과 피드백을 모두 입력해주세요.")
        else:
            st.error("해당 학번을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
