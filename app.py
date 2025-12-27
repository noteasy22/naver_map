import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 1. 디자인 적용 (style.css 불러오기) ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 페이지 설정 (브라우저 탭 이름 등)
st.set_page_config(page_title="Naver Kin Monitor", layout="wide")
local_css("style.css")

# --- 2. 로그인 상태 관리 세션 설정 ---
if 'login_open' not in st.session_state:
    st.session_state['login_open'] = False

# --- 3. 최상단 레이아웃 (로그인 버튼 배치를 위한 컬럼) ---
# 왼쪽은 비워두고(10), 오른쪽 끝에 버튼 배치(1.5)
top_empty, top_login = st.columns([10, 1.5])

with top_login:
    if st.button("로그인 🔑", use_container_width=True):
        st.session_state['login_open'] = not st.session_state['login_open']

# 로그인 버튼 클릭 시 나타나는 입력 창
if st.session_state['login_open']:
    with st.container(border=True):
        st.subheader("사용자 인증")
        l_id = st.text_input("아이디(이메일)", placeholder="user@example.com")
        l_pw = st.text_input("비밀번호", type="password")
        
        btn_l1, btn_l2 = st.columns(2)
        with btn_l1:
            if st.button("접속하기", use_container_width=True):
                st.success(f"{l_id}님, 접속되었습니다.")
                st.session_state['login_open'] = False
        with btn_l2:
            if st.button("창 닫기", use_container_width=True):
                st.session_state['login_open'] = False

# --- 4. 메인 화면 구성 (기존 기능 유지) ---
st.title("🛡️ 지식인 실시간 모니터링 대시보드")

# 오늘의 핫토픽 (CSS에서 너비가 자동으로 조절됩니다)
st.info("🔥 오늘의 핫토픽: 파이썬 에러 해결 방법, 지식인 마케팅 사례, 2025 데이터 공모전 전략 등")

# 데이터 로드
@st.cache_data
def load_data():
    if os.path.exists("kin_sample_data.csv"):
        return pd.read_csv("kin_sample_data.csv")
    else:
        # 데이터가 없을 경우 샘플 데이터 생성
        return pd.DataFrame({
            'category': ['IT/기술', '건강', '법률'],
            'title': ['샘플 질문입니다', '건강 관련 문의', '법률 상담'],
            'score': [85, 90, 70],
            'question': ['내용1', '내용2', '내용3'],
            'answer': ['답변1', '답변2', '답변3'],
            'collected_at': ['2025-12-27', '2025-12-27', '2025-12-27']
        })

df = load_data()

# 사이드바 설정
st.sidebar.title("🔍 Naver Kin Monitor")
category_list = ["전체"] + list(df['category'].unique()) if 'category' in df.columns else ["전체"]
category = st.sidebar.selectbox("카테고리 선택", category_list)

st.markdown("네이버 지식인의 질문/답변 데이터를 실시간으로 분석하여 신뢰도를 측정합니다.")

# 상단 메트릭
col1, col2, col3 = st.columns(3)
col1.metric("오늘 수집된 질문", f"{len(df)}개", "+12%")
col2.metric("평균 신뢰도 점수", f"{df['score'].mean():.1f}점", "-2.4점")
col3.metric("주의 필요 답변", "14개", "신규 3")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📡 실시간 모니터링", "🏆 신뢰도 랭킹", "📊 데이터 통계"])

with tab1:
    st.subheader("실시간 수집 현황")
    search_query = st.text_input("질문 제목 검색", placeholder="키워드를 입력하세요...")

    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, na=False)]

    for idx, row in filtered_df.iterrows():
        with st.container(border=True): # 카드 스타일 적용
            st.write(f"**[{row['category']}] {row['title']}**")
            st.write(f"신뢰도 점수: {row['score']}점")
            if st.button(f"상세보기 #{idx}", key=f"btn_{idx}"):
                st.write(f"**질문 내용:** {row['question']}")
                st.write(f"**답변 요약:** {row['answer']}")
                st.divider()

# 하단 리포트 섹션
st.divider()
st.subheader("🚩 최근 분석된 불성실 응답 상세 리포트")
report_col1, report_col2 = st.columns([2, 1])

with report_col1:
    st.write("**분석 대상:** [IT/기술] 파이썬 코드가 안 돌아가요...")
    st.error("⚠️ 광고성 링크 포함 및 질문과 무관한 답변 패턴 감지")
    st.text_area("AI 분석 의견", "해당 답변은 특정 웹사이트 홍보를 목적으로 작성된 것으로 판단됨. 답변의 80% 이상이 기존 홍보 문구와 일치함.", height=100)

with report_col2:
    st.metric("불성실 지수", "92%", delta="매우 높음", delta_color="inverse")
    st.button("신고하기", use_container_width=True, key="report_btn")
