import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import uuid
import pandas as pd

# 문서 폴더 경로 설정
documents_path = os.path.expanduser("~/Documents")
env_path = os.path.join(documents_path, "test.env")

# test.env 파일에서 환경 변수 로드
load_dotenv(env_path)

# OpenAI API 키 설정
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # GPT-4 mini 모델 사용
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {str(e)}")
        return None

def initialize_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

def main():
    initialize_session_state()

    st.set_page_config(page_title="학생 기록 보완 시스템", page_icon="📝", layout="wide")
    
    st.title("📚 학생 기록 보완 시스템")
    st.write("학생의 성취 수준, 관찰 내용, 역량 등을 입력하면 AI가 보완된 기록을 제안합니다.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("학생 정보 입력")
        achievement_standards = st.text_area("성취기준:", height=100)
        student_achievement = st.text_area("학생의 성취 수준 및 관찰 내용:", height=150)
        
        competencies = [
            "자기관리 역량", "지식정보처리 역량", "창의적 사고 역량", "심미적 감성 역량", 
            "의사소통 역량", "공동체 역량", "비판적 사고력", "문제 해결 및 혁신 능력"
        ]
        observed_competencies = st.multiselect("관찰된 역량:", competencies)
        
        if st.button("기록 보완 요청", key=f"submit_button_{st.session_state.user_id}"):
            if achievement_standards and student_achievement:
                with st.spinner("AI가 보완된 기록을 생성 중입니다..."):
                    messages = [
                        {"role": "system", "content": """당신은 학생 기록을 보완하는 전문 교육 AI 조교입니다. 
                        제공된 정보를 바탕으로 객관적이고 구체적인 학생 기록을 보완하여 작성해주세요. 
                        학생의 강점을 부각시키고, 기록에 대해 개선이 필요한 부분은 건설적으로 제안해주세요."""},
                        {"role": "user", "content": f"""
                        성취기준: {achievement_standards}
                        학생의 성취 수준 및 관찰 내용: {student_achievement}
                        관찰된 역량: {', '.join(observed_competencies)}

                        다음 형식으로 보완된 학생 기록을 작성해주세요:
                        1. 성취 수준 분석
                        2. 관찰된 역량 설명
                        3. 학생의 강점
                        4. 개선이 필요한 부분
                        5. 학생 기록 작성 방향 제안
                        """}
                    ]
                    response = generate_response(messages)
                    if response:
                        st.session_state.conversation_history.append({"input": student_achievement, "output": response})
                        with col2:
                            st.subheader("보완된 학생 기록")
                            st.write(response)
            else:
                st.warning("성취기준과 학생의 성취 수준 및 관찰 내용을 모두 입력해주세요.")

    # 대화 기록 표시
    if st.session_state.conversation_history:
        with col2:
            st.subheader("기록 이력")
            for entry in st.session_state.conversation_history:
                st.text("입력:")
                st.write(entry["input"])
                st.text("AI 보완 기록:")
                st.write(entry["output"])
                st.markdown("---")

    # 데이터 다운로드 기능
    if st.session_state.conversation_history:
        df = pd.DataFrame(st.session_state.conversation_history)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="기록 이력 다운로드",
            data=csv,
            file_name="student_records.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
