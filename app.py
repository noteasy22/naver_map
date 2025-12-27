import streamlit as st
import pandas as pd
import os
import re
from collections import Counter

# 1. 페이지 설정
st.set_page_config(page_title="Naver KiN Insight", layout="wide")

# 외부 CSS 로드 함수
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_doc_id' not in st.session_state:
    st.session_state.selected_doc_id = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""

# 2. 데이터 로드
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'kin_sample_data.csv')
    if not os.path.exists(file_path):
        return None
    df = pd.read_csv(file_path)
    df['제목'] = df['제목'].fillna("제목 없음").astype(str)
    df['질문내용'] = df['질문내용'].fillna("내용 없음").astype(str)
    df['답변내용'] = df['답변내용'].fillna("").astype(str)
    df['조회수'] = pd.to_numeric(df['조회수'], errors='coerce').fillna(0)
    return df

df = load_data()

# 3. 신뢰도 계산 엔진
def calculate_reliability(row):
    score = 100
    ans = str(row['답변내용'])
    if len(ans) < 20: score -= 40
    if any(word in ans for word in ['광고', '모르겠네요', '내공냠냠']): score -= 50
    if row['싫어요'] > row['좋아요']: score -= 30
    return max(0, score)

def get_traffic_light(score):
    if score >= 70: return "🟢 (안전)", "green"
    elif score >= 40: return "🟡 (주의)", "orange"
    else: return "🔴 (위험)", "red"

# --- 페이지 로직 ---

if st.session_state.page != 'main':
    if st.button("🏠 메인으로", key="main_btn"):
        st.session_state.page = 'main'
        st.session_state.selected_doc_id = None
        st.rerun()

# [메인 페이지]
if st.session_state.page == 'main':
    col_t1, col_t2 = st.columns([8, 2])
    with col_t1:
        st.title("🔍 지식인 클린 가이드")
    with col_t2:
        if st.button("🙋 나의 질문 모아보기", use_container_width=True):
            st.session_state.page = 'my_questions'
            st.rerun()

    search_input = st.text_input("검색어를 입력하세요", value=st.session_state.search_query)

    # --- 실시간 해시태그 ---
    if df is not None:
        all_text = " ".join(df['질문내용'].astype(str).tolist())
        words_only = re.findall(r'[가-힣]{2,}', all_text)
        stop_words = ['제가', '저는', '있나요', '궁금합니다', '알려주세요', '어떻게', '하면', '하고', '오늘', '진짜', '관련']
        filtered_words = [w for w in words_only if w not in stop_words]
        top_4_tags = [tag for tag, count in Counter(filtered_words).most_common(4)]

        tag_cols = st.columns([0.8, 0.8, 0.8, 0.8, 6])
        for i, tag in enumerate(top_4_tags):
            if tag_cols[i].button(f"#{tag}", key=f"htag_{tag}"):
                st.session_state.search_query = tag
                st.rerun()

    st.divider()

    col_left, col_right = st.columns([7, 3])

    with col_right:
        st.subheader("🔥 오늘의 핫토픽")
        df_unique = df.drop_duplicates('doc_id')
        words = " ".join(df_unique['제목']).split()
        most_common = Counter([w for w in words if len(w) > 1]).most_common(5)
        for i, (word, count) in enumerate(most_common):
            if st.button(f"{i+1}. {word} ({count}건)", key=f"hot_{word}", use_container_width=True):
                st.session_state.search_query = word
                st.rerun()
        
        st.write("")
        st.subheader("🔝 실시간 인기 질문")
        rank_df = df.groupby('doc_id').agg({
            '제목': 'first', 
            '조회수': 'max', 
            '답변순번': 'max'
        }).sort_values(by='답변순번', ascending=False).head(5)
        
        st.dataframe(
            rank_df[['제목', '조회수', '답변순번']].rename(columns={'답변순번': '답변수'}),
            hide_index=True,
            use_container_width=True
        )

    with col_left:
        current_query = search_input if search_input else st.session_state.search_query
        if len(current_query) >= 2:
            st.subheader(f"🔎 '{current_query}' 검색 결과")
            search_res = df_unique[df_unique['제목'].str.contains(current_query) | df_unique['질문내용'].str.contains(current_query)]
            for _, row in search_res.iterrows():
                c1, c2 = st.columns([8, 2])
                if c1.button(f"📄 {row['제목']}", key=f"res_{row['doc_id']}", use_container_width=True):
                    st.session_state.selected_doc_id = row['doc_id']
                    st.session_state.page = 'detail'
                    st.rerun()
                c2.write(f"👁️ {int(row['조회수'])}")
                st.divider()

# [상세 보기]
elif st.session_state.page == 'detail':
    doc_id = st.session_state.selected_doc_id
    q_data = df[df['doc_id'] == doc_id].iloc[0]
    answers = df[df['doc_id'] == doc_id]

    st.sidebar.header("🛡️ 답변 신뢰도 분석")
    for _, ans_row in answers.iterrows():
        score = calculate_reliability(ans_row)
        label, color = get_traffic_light(score)
        with st.sidebar.expander(f"답변 #{ans_row['답변순번']} 지표"):
            st.markdown(f"**상태:** :{color}[{label}]")
            st.metric("신뢰 점수", f"{score}%")
            if st.sidebar.button(f"👍 유용함 투표", key=f"v_{ans_row['doc_id']}_{ans_row['답변순번']}"):
                st.toast("투표가 반영되었습니다!")
            st.divider()

    st.title(f"Q: {q_data['제목']}")
    st.write(f"👁️ 조회수: {int(q_data['조회수'])} | 📅 수집일: {q_data['collected_at']}")
    st.info(f"**질문내용:** {q_data['질문내용']}")
    
    st.subheader(f"💬 답변 목록 ({len(answers)}개)")
    for _, ans_row in answers.iterrows():
        with st.chat_message("user"):
            st.write(ans_row['답변내용'])
            st.caption(f"좋아요: {ans_row['좋아요']} | 싫어요: {ans_row['싫어요']} | 순번: {ans_row['답변순번']}")

# [나의 질문 목록 페이지]
elif st.session_state.page == 'my_questions':
    st.title("🙋 나의 질문 모아보기")
    my_q_list = df.drop_duplicates('doc_id').head(3) 
    
    for _, row in my_q_list.iterrows():
        with st.container():
            col_q, col_btn = st.columns([8, 2])
            col_q.subheader(f"📌 {row['제목']}")
            col_q.write(f"답변수: {df[df['doc_id']==row['doc_id']]['답변순번'].max()}개")
            if col_btn.button("상세 분석 보기", key=f"my_view_{row['doc_id']}", use_container_width=True):
                st.session_state.selected_doc_id = row['doc_id']
                st.session_state.page = 'detail'
                st.rerun()
            st.divider()
