import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태(데이터 저장소) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="나의 용돈기입장", page_icon="💰", layout="wide"
)

# 파스텔 색상 목록 정의 (이름: HEX 색상코드)
PASTEL_COLORS = {
    "기본 (화이트)": "#FFFFFF",
    "파스텔 핑크": "#FFD1DC",
    "파스텔 블루": "#AEC6CF",
    "파스텔 그린": "#B2AC88",
    "파스텔 옐로우": "#FDFD96",
    "파스텔 퍼플": "#C3B1E1",
    "파스텔 피치": "#FFDAB9",
}

# 사이드바에 배경색 선택 드롭다운 박스 생성
selected_color_name = st.sidebar.selectbox(
    "🎨 배경 스타일 선택 (파스텔)", list(PASTEL_COLORS.keys())
)
bg_color = PASTEL_COLORS[selected_color_name]

# 선택한 파스텔 배경색을 앱 전체 스타일(CSS)에 적용
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 앱이 새로고침되어도 데이터가 유지되도록 Session State에 기본 데이터프레임 생성
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "날짜": [
                datetime.date.today(),
                datetime.date.today() - datetime.timedelta(days=2),
            ],
            "유형": ["수입", "지출"],
            "카테고리": ["용돈", "식비"],
            "금액": [50000, 8000],
            "내역": ["부모님 용돈", "점심 식사"],
        }
    )

st.title("💰 나의 스마트 용돈기입장")
st.write("수입과 지출을 기록하고 한눈에 관리해보세요!")

# -----------------------------------------------------------------------------
# 2. 사이드바: 새로운 내역 입력 폼
# -----------------------------------------------------------------------------
st.sidebar.divider()
st.sidebar.header("📝 내역 추가하기")

with st.sidebar.form("entry_form", clear_on_submit=True):
    date_input = st.date_input("날짜 선택", datetime.date.today())
    type_input = st.radio("유형 선택", ["지출", "수입"], horizontal=True)

    # 유형에 따른 카테고리 옵션 설정
    if type_input == "지출":
        category_options = [
            "식비",
            "교통비",
            "쇼핑",
            "문화/취미",
            "기타 지출",
        ]
    else:
        category_options = ["용돈", "상여금", "금융수익", "기타 수입"]

    category_input = st.selectbox("카테고리", category_options)
    amount_input = st.number_input(
        "금액 (원)", min_value=0, step=1000, value=0
    )
    memo_input = st.text_input("사유 및 상세 내역", placeholder="예: 친구와 저녁 식사")

    submit_button = st.form_submit_button("저장하기")

# 저장 버튼 클릭 시 세션 상태의 데이터프레임에 추가
if submit_button:
    if amount_input > 0:
        new_data = pd.DataFrame(
            [
                {
                    "날짜": date_input,
                    "유형": type_input,
                    "카테고리": category_input,
                    "금액": amount_input,
                    "내역": memo_input,
                }
            ]
        )
        st.session_state.df = pd.concat(
            [st.session_state.df, new_data], ignore_index=True
        )
        st.sidebar.success("성공적으로 저장되었습니다!")
    else:
        st.sidebar.error("금액을 0원 이상 입력해 주세요.")

# -----------------------------------------------------------------------------
# 3. 메인 화면: 탭 구성 (내역 목록, 차트 분석, 월별/일별 조회)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📋 전체 내역 목록", "📊 수입/지출 분석 차트", "📅 날짜별 상세 조회"]
)

# -----------------------------------------------------------------------------
# [TAB 1] 전체 내역 목록 및 요약
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("전체 거래 내역")

    # 총 수입, 총 지출, 잔액 계산
    total_income = st.session_state.df[
        st.session_state.df["유형"] == "수입"
    ]["금액"].sum()
    total_expense = st.session_state.df[
        st.session_state.df["유형"] == "지출"
    ]["금액"].sum()
    balance = total_income - total_expense

    # 요약지표 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("총 수입", f"{total_income:,} 원")
    col2.metric("총 지출", f"{total_expense:,} 원")
    col3.metric("현재 잔액", f"{balance:,} 원")

    st.divider()

    # 데이터프레임 날짜순 정렬 후 출력
    sorted_df = st.session_state.df.sort_values(
        by="날짜", ascending=False
    ).reset_index(drop=True)
    st.dataframe(sorted_df, use_container_width=True)

# -----------------------------------------------------------------------------
# [TAB 2] 수입/지출 시각화 차트 (Plotly 활용)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("수입 및 지출 분석")

    if not st.session_state.df.empty:
        col_chart1, col_chart2 = st.columns(2)

        # 1. 지출 카테고리별 원형 차트
        with col_chart1:
            expense_df = st.session_state.df[
                st.session_state.df["유형"] == "지출"
            ]
            if not expense_df.empty:
                fig_expense = px.pie(
                    expense_df,
                    values="금액",
                    names="카테고리",
                    title="지출 카테고리별 비중",
                    hole=0.4,
                )
                st.plotly_chart(fig_expense, use_container_width=True)
            else:
                st.info("지출 내역이 없습니다.")

        # 2. 수입 카테고리별 원형 차트
        with col_chart2:
            income_df = st.session_state.df[
                st.session_state.df["유형"] == "수입"
            ]
            if not income_df.empty:
                fig_income = px.pie(
                    income_df,
                    values="금액",
                    names="카테고리",
                    title="수입 카테고리별 비중",
                    hole=0.4,
                )
                st.plotly_chart(fig_income, use_container_width=True)
            else:
                st.info("수입 내역이 없습니다.")

        st.divider()

        # 3. 날짜별 수입/지출 막대 차트
        st.subheader("일자별 수입 및 지출 추이")
        daily_df = (
            st.session_state.df.groupby(["날짜", "유형"])["금액"]
            .sum()
            .reset_index()
        )
        fig_bar = px.bar(
            daily_df,
            x="날짜",
            y="금액",
            color="유형",
            barmode="group",
            title="일자별 수입/지출 비교",
            color_discrete_map={"수입": "#2ECC71", "지출": "#E74C3C"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.info("차트를 표시할 데이터가 없습니다.")

# -----------------------------------------------------------------------------
# [TAB 3] 날짜별 상세 조회 (기본 Streamlit 컴포넌트 활용)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("특정 기간 내역 조회")

    # 조회할 기간 선택
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("시작일", datetime.date.today().replace(day=1))
    with col_date2:
        end_date = st.date_input("종료일", datetime.date.today())

    # 선택한 날짜에 맞춰 데이터 필터링
    mask = (st.session_state.df["날짜"] >= start_date) & (
        st.session_state.df["날짜"] <= end_date
    )
    filtered_df = st.session_state.df.loc[mask]

    st.divider()

    if not filtered_df.empty:
        selected_income = filtered_df[filtered_df["유형"] == "수입"]["금액"].sum()
        selected_expense = filtered_df[filtered_df["유형"] == "지출"]["금액"].sum()

        st.write(f"**선택 기간 총 수입:** {selected_income:,}원 | **총 지출:** {selected_expense:,}원")
        st.dataframe(
            filtered_df.sort_values(by="날짜", ascending=False).reset_index(drop=True),
            use_container_width=True,
        )
    else:
        st.info("해당 기간에 기록된 내역이 없습니다.")
