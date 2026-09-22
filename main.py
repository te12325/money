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
            ],
            "유형": ["수입", "지출"],
            "카테고리": ["용돈", "간식비"],
            "금액": [50000, 8000],
            "내역": ["부모님 용돈", "편의점 이용"],
        }
    )

st.title("💰 나의 스마트 용돈기입장")
st.write("수입과 지출을 기록하고 한눈에 관리해보세요!")

# -----------------------------------------------------------------------------
# 2. 사이드바: 새로운 내역 입력 폼 (카테고리 직접 입력 지원)
# -----------------------------------------------------------------------------
st.sidebar.header("📝 내역 추가하기")

with st.sidebar.form("entry_form", clear_on_submit=True):
    date_input = st.date_input("날짜 선택", datetime.date.today())
    type_input = st.radio("유형 선택", ["지출", "수입"], horizontal=True)

    # 드롭다운 대신 사용자가 직접 카테고리를 작성할 수 있는 텍스트 입력창
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
# 3. 메인 화면: 탭 구성 (내역 목록, 차트 분석, 날짜별 상세 조회)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📋 전체 내역 목록", "📊 수입/지출 분석 차트", "📅 날짜별 상세 조회"]
)

# -----------------------------------------------------------------------------
# [TAB 1] 전체 내역 목록 및 요약 (수입: 파란색, 지출: 빨간색 하이라이트)
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

    # 요약지표 표시 (수입: 기본/파란색 톤, 지출: 빨간색 delta 적용)
    col1, col2, col3 = st.columns(3)
    col1.metric("총 수입 (파랑)", f"{total_income:,} 원")
    col2.metric("총 지출 (빨강)", f"{total_expense:,} 원", delta=f"-{total_expense:,} 원", delta_color="inverse")
    col3.metric("현재 잔액", f"{balance:,} 원")

    st.divider()

    # 데이터프레임 날짜순 정렬
    sorted_df = st.session_state.df.sort_values(
        by="날짜", ascending=False
    ).reset_index(drop=True)

    # 수입(파란색), 지출(빨간색) 텍스트 색상 스타일 적용 함수
    def highlight_type(row):
        if row["유형"] == "수입":
            return ["color: #3182CE; font-weight: bold;"] * len(row)
        elif row["유형"] == "지출":
            return ["color: #E53E3E; font-weight: bold;"] * len(row)
        return [""] * len(row)

    styled_df = sorted_df.style.apply(highlight_type, axis=1).format({"금액": "{:,} 원"})
    st.dataframe(styled_df, use_container_width=True)

# -----------------------------------------------------------------------------
# [TAB 2] 수입/지출 시각화 차트 (파란색/빨간색 테마 적용)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("수입 및 지출 분석")

    if not st.session_state.df.empty:
        col_chart1, col_chart2 = st.columns(2)

        # 1. 지출 카테고리별 원형 차트 (빨간색 계열)
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

        # 2. 수입 카테고리별 원형 차트 (파란색 계열)
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

        # 3. 일자별 수입/지출 막대 차트 (수입: 파란색 #3182CE, 지출: 빨간색 #E53E3E)
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
# [TAB 3] 날짜별 상세 조회
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("특정 기간 내역 조회")

    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("시작일", datetime.date.today().replace(day=1))
    with col_date2:
        end_date = st.date_input("종료일", datetime.date.today())

    # 선택 기간 필터링
    mask = (st.session_state.df["날짜"] >= start_date) & (
        st.session_state.df["날짜"] <= end_date
    )
    filtered_df = st.session_state.df.loc[mask]

    st.divider()

    if not filtered_df.empty:
        selected_income = filtered_df[filtered_df["유형"] == "수입"]["금액"].sum()
        selected_expense = filtered_df[filtered_df["유형"] == "지출"]["금액"].sum()

        st.write(
            f"**선택 기간 총 수입:** <span style='color:#3182CE;'>{selected_income:,}원</span> | "
            f"**총 지출:** <span style='color:#E53E3E;'>{selected_expense:,}원</span>",
            unsafe_allow_html=True,
        )

        sorted_filtered = filtered_df.sort_values(
            by="날짜", ascending=False
        ).reset_index(drop=True)
        styled_filtered = sorted_filtered.style.apply(highlight_type, axis=1).format({"금액": "{:,} 원"})
        st.dataframe(styled_filtered, use_container_width=True)
    else:
        st.info("해당 기간에 기록된 내역이 없습니다.")
