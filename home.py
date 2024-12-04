import streamlit as st
from pymongo import MongoClient

# MongoDB 연결 설정
MONGO_URI = "mongodb+srv://jsheek93:j103203j@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

evaluation_db = client["teacher_page"]
teacher_user_collection = evaluation_db["teacher_user"]

def main():
    st.title("온양고등학교 관리자용 페이지")

    # 로그인과 회원가입 탭 분리
    tabs = st.tabs(["교사 로그인", "교사 회원가입"])

    # 회원가입 탭
    with tabs[1]:
        st.subheader("교사 회원가입")
        username = st.text_input("아이디", key="signup_username")
        password = st.text_input("비밀번호", type="password", key="signup_password")
        name = st.text_input("이름", key="signup_name")
        position = st.selectbox("직위", ["교장", "교감", "교사"], key="signup_position")

        if st.button("회원가입", key="signup_button"):
            if username and password and name and position:
                # 입력받은 정보 저장
                user_data = {
                    "username": username,
                    "password": password,
                    "name": name,
                    "position": position
                }
                teacher_user_collection.insert_one(user_data)
                st.success("회원가입이 완료되었습니다!")
            else:
                st.error("모든 필드를 입력해주세요.")

    # 로그인 탭
    with tabs[0]:
        st.subheader("교사 로그인")
        login_username = st.text_input("아이디", key="login_username")
        login_password = st.text_input("비밀번호", type="password", key="login_password")

        if st.button("로그인", key="login_button"):
            if login_username and login_password:
                # 로그인 로직 (예: 사용자 인증)
                user = teacher_user_collection.find_one({"username": login_username, "password": login_password})
                if user:
                    st.success(f"{user['name']}님, 로그인에 성공하였습니다!")
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
            else:
                st.error("아이디와 비밀번호를 입력해주세요.")

if __name__ == "__main__":
    main()
