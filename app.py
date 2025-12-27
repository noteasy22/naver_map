import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- [추가] 외부 디자인 파일(style.css)을 불러오는 함수 ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 디자인 적용 (style.css 파일을 읽어옵니다)
local_css("style.css")

# --- 기존 기능 로직 (변경 없음) ---
# 데이터 로드
@st.cache_data
def load_data():
    # 파일명이 kin_sample_data.csv인지 확인해주세요
    df = pd.read_csv("kin_sample_data.csv")
    return df

df = load_data()

# 사이드바 설정
st.sidebar.title("🔍 Naver Kin Monitor")
category = st.sidebar.selectbox("카테고리 선택", ["전체", "건강", "법률", "교육", "IT/기술"])

# 메인 화면 타이틀
st.title("🛡️ 지식인 실시간 모니터링 대시보드")
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

    # 필터링 로직
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_query, na=False)]

    # 리스트 출력
    for idx, row in filtered_df.iterrows():
        with st.container():
            st.info(f"**[{row['category']}] {row['title']}** (신뢰도: {row['score']}점)")
            if st.button(f"상세보기 #{idx}", key=f"btn_{idx}"):
                st.write(f"**질문 내용:** {row['question']}")
                st.write(f"**답변 요약:** {row['answer']}")
                st.divider()

# 하단: 최근 분석된 불성실 응답 리포트
st.divider()
st.subheader("🚩 최근 분석된 불성실 응답 상세 리포트")
report_col1, report_col2 = st.columns([2, 1])

with report_col1:
    st.write("**분석 대상:** [IT/기술] 파이썬 코드가 안 돌아가요...")
    st.error("⚠️ 광고성 링크 포함 및 질문과 무관한 답변 패턴 감지")
    st.text_area("AI 분석 의견", "해당 답변은 특정 웹사이트 홍보를 목적으로 작성된 것으로 판단됨. 답변의 80% 이상이 기존 홍보 문구와 일치함.", height=100)

with report_col2:
    st.metric("불성실 지수", "92%", delta="매우 높음", delta_color="inverse")
    st.button("신고하기", use_container_width=True)
