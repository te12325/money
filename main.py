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

# 세션 상태에 기본 데이터프레임 초기화
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "날짜": [
                datetime.date.today(),
                datetime.date.today() - datetime.timedelta(days=2),
                datetime.date.today() - datetime.timedelta(days=5),
            ],
            "유형": ["수입", "지출", "지출"],
            "카테고리": ["용돈", "간식비", "교통비"],
            "금액": [100000, 8000, 15000],
            "내역": ["부모님 용돈", "편의점 이용", "버스/지하철 충전"],
        }
    )

st.title("💰 나의 스마트 용돈기입장")
st.write("수입과 지출을 기록하고 한눈에 관리해보세요!")

# -----------------------------------------------------------------------------
# 2. 사이드바: 새로운 내역 입력 폼
# -----------------------------------------------------------------------------
st.sidebar.header("📝 내역 추가하기")

with st.sidebar.form("entry_form", clear_on_submit=True):
    date_input = st.date_input("날짜 선택", datetime.date.today())
    type_input = st.radio("유형 선택", ["지출", "수입"], horizontal=True)

    category_input = st.text_input(
        "카테고리 직접 입력", placeholder="예: 간식비, 택시비, 알바비 등"
    )

    amount_input = st.number_input(
        "금액 (원)", min_value=0, step=1000, value=0
    )
    memo_input = st.text_input("사유 및 상세 내역", placeholder="예: 친구와 카페 방문")

    submit_button = st.form_submit_button("저장하기")

# 저장 버튼 클릭 시 세션 상태 데이터프레임에 데이터 추가
if submit_button:
    if not category_input.strip():
        st.sidebar.error("카테고리를 입력해 주세요.")
    elif amount_input <= 0:
        st.sidebar.error("금액을 0원 이상 입력해 주세요.")
    else:
        new_data = pd.DataFrame(
            [
                {
                    "날짜": date_input,
                    "유형": type_input,
                    "카테고리": category_input.strip(),
                    "금액": amount_input,
                    "내역": memo_input,
                }
            ]
        )
        st.session_state.df = pd.concat(
            [st.session_state.df, new_data], ignore_index=True
        )
        st.sidebar.success("성공적으로 저장되었습니다!")

# -----------------------------------------------------------------------------
# 3. 메인 화면: 탭 구성 (내역 목록, 차트 분석, 이번 달 요약)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📋 전체 내역 목록", "📊 수입/지출 분석 차트", "🏆 이달의 수입/지출 요약"]
)

# -----------------------------------------------------------------------------
# [TAB 1] 전체 내역 목록 (유형 컬럼만 파란색/빨간색, 나머지는 검정색)
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("전체 거래 내역")

    # 총 수입, 총 지출, 현재 잔액 계산
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

    # 데이터프레임 날짜순 정렬
    sorted_df = st.session_state.df.sort_values(
        by="날짜", ascending=False
    ).reset_index(drop=True)

    # '유형' 컬럼만 수입=파란색, 지출=빨간색으로 설정하는 스타일 함수
    def highlight_type_only(val):
        if val == "수입":
            return "color: #3182CE; font-weight: bold;"
        elif val == "지출":
            return "color: #E53E3E; font-weight: bold;"
        return ""

    styled_df = sorted_df.style.map(
        highlight_type_only, subset=["유형"]
    ).format({"금액": "{:,} 원"})
    
    st.dataframe(styled_df, use_container_width=True)

# -----------------------------------------------------------------------------
# [TAB 2] 수입/지출 시각화 차트
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
                    title="🔴 지출 카테고리별 비중",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Reds_r,
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
                    title="🔵 수입 카테고리별 비중",
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                )
                st.plotly_chart(fig_income, use_container_width=True)
            else:
                st.info("수입 내역이 없습니다.")

        st.divider()

        # 3. 일자별 수입/지출 막대 차트 (수입: 파란색, 지출: 빨간색)
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
            title="일자별 수입 vs 지출 비교",
            color_discrete_map={"수입": "#3182CE", "지출": "#E53E3E"},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.info("차트를 표시할 데이터가 없습니다.")

# -----------------------------------------------------------------------------
# [TAB 3] 이달의 누적 수입/지출 및 최대 항목 분석
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📅 이번 달 누적 분석 & 최다 항목")

    # 오늘 기준 이번 달 데이터만 필터링
    today = datetime.date.today()
    df_copy = st.session_state.df.copy()
    df_copy["날짜"] = pd.to_datetime(df_copy["날짜"])

    month_mask = (df_copy["날짜"].dt.year == today.year) & (
        df_copy["날짜"].dt.month == today.month
    )
    this_month_df = st.session_state.df.loc[month_mask]

    if not this_month_df.empty:
        # 이번 달 누적 수입 / 지출
        m_income = this_month_df[this_month_df["유형"] == "수입"]["금액"].sum()
        m_expense = this_month_df[this_month_df["유형"] == "지출"]["금액"].sum()

        col_m1, col_m2 = st.columns(2)
        col_m1.metric(f"{today.month}월 누적 수입", f"{m_income:,} 원")
        col_m2.metric(f"{today.month}월 누적 지출", f"{m_expense:,} 원")

        st.divider()

        col_top1, col_top2 = st.columns(2)

        # 가장 돈을 많이 쓴 카테고리 및 내역 구하기
        with col_top1:
            st.markdown("### 🔴 어디에 가장 많이 썼을까?")
            m_expense_df = this_month_df[this_month_df["유형"] == "지출"]

            if not m_expense_df.empty:
                # 1. 가장 지출이 컸던 카테고리
                top_cat_exp = (
                    m_expense_df.groupby("카테고리")["금액"]
                    .sum()
                    .idxmax()
                )
                top_cat_exp_amt = m_expense_df.groupby("카테고리")["금액"].sum().max()

                # 2. 가장 지출이 컸던 단일 내역
                max_exp_row = m_expense_df.loc[m_expense_df["금액"].idxmax()]

                st.info(
                    f"**가장 지출이 많은 카테고리:**\n\n"
                    f"👉 **{top_cat_exp}** ({top_cat_exp_amt:,}원)"
                )
                st.warning(
                    f"**가장 큰 단일 지출 내역:**\n\n"
                    f"👉 **{max_exp_row['내역']}** ({max_exp_row['금액']:,}원 / {max_exp_row['카테고리']})"
                )
            else:
                st.write("이번 달 지출 내역이 없습니다.")

        # 가장 돈을 많이 번 카테고리 및 내역 구하기
        with col_top2:
            st.markdown("### 🔵 어디서 가장 많이 들어왔을까?")
            m_income_df = this_month_df[this_month_df["유형"] == "수입"]

            if not m_income_df.empty:
                # 1. 가장 수입이 컸던 카테고리
                top_cat_inc = (
                    m_income_df.groupby("카테고리")["금액"]
                    .sum()
                    .idxmax()
                )
                top_cat_inc_amt = m_income_df.groupby("카테고리")["금액"].sum().max()

                # 2. 가장 수입이 컸던 단일 내역
                max_inc_row = m_income_df.loc[m_income_df["금액"].idxmax()]

                st.info(
                    f"**가장 수입이 많은 카테고리:**\n\n"
                    f"👉 **{top_cat_inc}** ({top_cat_inc_amt:,}원)"
                )
                st.warning(
                    f"**가장 큰 단일 수입 내역:**\n\n"
                    f"👉 **{max_inc_row['내역']}** ({max_inc_row['금액']:,}원 / {max_inc_row['카테고리']})"
                )
            else:
                st.write("이번 달 수입 내역이 없습니다.")

    else:
        st.info("이번 달에 등록된 내역이 없습니다.")
