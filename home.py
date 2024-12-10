import streamlit as st
from pymongo import MongoClient

# MongoDB 객을 설정
MONGO_URI = "mongodb+srv://jsheek93:j103203j@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)

evaluation_db = client["teacher_page"]
teacher_user_collection = evaluation_db["teacher_user"]

def main():
    # 스타일 추가
    st.markdown(
        """
        <style>
        body {
            background-color: #f0f2f6;
            font-family: Arial, sans-serif;
        }
        .main-title {
            color: #333;
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 20px;
        }
        .sub-title {
            color: #4f8df5;
            font-size: 1.5em;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='main-title' style='font-weight: bold;'>공주고등학교 관리자용 페이지</div>", unsafe_allow_html=True)
    st.sidebar.image("image.png", use_container_width=True)
    # 로그인과 회원가입 탭 분리
    tabs = st.tabs(["교사 로그인", "교사 회원가입"])

    # 회원가입 탭
    with tabs[1]:
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
        login_username = st.text_input("아이디", key="login_username")
        login_password = st.text_input("비밀번호", type="password", key="login_password")

        if st.button("로그인", key="login_button"):
            if login_username and login_password:
                # 로그인 로직 (예: 사용자 인증)
                user = teacher_user_collection.find_one({"username": login_username, "password": login_password})
                if user:
                    st.success(f"{user['name']}님 환영합니다!")
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
            else:
                st.error("아이디와 비밀번호를 입력해주세요.")

if __name__ == "__main__":
    main()
