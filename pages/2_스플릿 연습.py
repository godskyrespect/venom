import streamlit as st
from pymongo import MongoClient

# MongoDB 연결 설정
MONGO_URI = "mongodb+srv://jsheek93:j103203j@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

# 데이터베이스 및 컬렉션 연결
highschool_db = client["highschool_db"]
classes_info_collection = highschool_db["classes_info"]

# Streamlit 페이지 설정
st.title("Highschool Classes Information")
st.subheader("Classes List")

# MongoDB에서 데이터를 가져오기
classes_data = classes_info_collection.find_one({"_id": 20241001})

# 데이터를 Streamlit에 표시
if classes_data:
    classes = classes_data.get("classes", [])
    for class_info in classes:
        st.write(f"Class ID: {class_info['class_id']}")
        st.write(f"Class Name: {class_info['class_name']}")
        st.write(f"Professor: {class_info['professor']}")
        
        # achievements 문자열을 쌍따옴표 단위로 배열로 변환하고 출력
        achievements_str = class_info.get("achievements", "")
        achievements_list = achievements_str.split('"')[1::2]
        st.write("Achievements:")
        for achievement in achievements_list:
            st.write(f"- {achievement.strip()}")
        
        st.write("---")
else:
    st.write("No classes information available.")
