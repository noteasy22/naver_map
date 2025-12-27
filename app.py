import streamlit as st
import pandas as pd
import os

# --- [디자인 추가] 외부 CSS 파일을 불러오는 함수 ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 페이지 설정 및 디자인 적용
st.set_page_config(layout="wide")
local_css("style.css")

# --- 1. 로그인 기능 (Share 버튼 옆 배치) ---
if 'login_open' not in st.session_state:
    st.session_state['login_open'] = False

t_col1, t_col2 = st.columns([10, 1.5])
with t_col2:
    if st.button("로그인 🔑", use_container_width=True):
        st.session_state['login_open'] = not st.session_state['login_open']

if st.session_state['login_open']:
    with st.container(border=True):
        st.subheader("사용자 인증")
        st.text_input("아이디", placeholder="user@example.com")
        st.text_input("비밀번호", type="password")
        if st.button("접속하기"):
            st.session_state['login_open'] = False

# --- 2. 데이터 로드 (에러 해결 핵심 코드 포함) ---
df = pd.read_csv("kin_sample_data.csv")
# [핵심] 컬럼 이름의 앞뒤 공백을 강제로 제거하여 KeyError를 방지합니다.
df.columns = df.columns.str.strip()

# --- 3. 기존 기능 코드 (그대로 유지) ---
st.title("🛡️ 지식인 실시간 모니터링 대시보드")

# 오늘의 핫토픽 (CSS에서 너비가 85%로 조절됨)
st.info("🔥 오늘의 핫토픽: 파이썬 에러 해결 방법, 지식인 마케팅 사례 등")

# 상단 메트릭
col1, col2, col3 = st.columns(3)
col1.metric("오늘 수집된 질문", f"{len(df)}개")
# 이제 'score'를 안전하게 찾을 수 있습니다.
col2.metric("평균 신뢰도 점수", f"{df['score'].mean():.1f}점") 
col3.metric("주의 필요 답변", "14개")

# 탭 구성 및 상세 내용
tab1, tab2, tab3 = st.tabs(["📡 실시간 모니터링", "🏆 신뢰도 랭킹", "📊 데이터 통계"])

with tab1:
    st.subheader("실시간 수집 현황")
    for idx, row in df.iterrows():
        with st.container(border=True):
            st.write(f"**[{row['category']}] {row['title']}**")
            if st.button(f"상세보기 #{idx}", key=f"btn_{idx}"):
                st.write(f"**질문:** {row['question']}")
                st.write(f"**답변:** {row['answer']}")

# 하단 리포트 (기존 기능 유지)
st.divider()
st.subheader("🚩 최근 분석된 불성실 응답 상세 리포트")
r_col1, r_col2 = st.columns([2, 1])
with r_col1:
    st.error("⚠️ 광고성 링크 포함 및 질문과 무관한 답변 패턴 감지")
with r_col2:
    st.metric("불성실 지수", "92%")
