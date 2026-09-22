import datetime
import calendar
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태(데이터 저장소) 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="용돈 기입장 💲", page_icon="💲", layout="wide"
)

# 세션 상태에 기본 데이터프레임 초기화
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(
        {
            "ID": [1, 2, 3],
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

st.title("💲 용돈 기입장")
st.write("수입과 지출을 손쉽게 기록하고 일별/월별로 한눈에 관리해보세요!")

# -----------------------------------------------------------------------------
# 2. 사이드바: 내역 추가 / 수정 / 삭제
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ 내역 관리")
action = st.sidebar.radio("작업 선택", ["📝 내역 추가", "✏️ 내역 수정", "🗑️ 내역 삭제"])

# --- [내역 추가] ---
if action == "📝 내역 추가":
    st.sidebar.subheader("새 내역 입력")
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

    if submit_button:
        if not category_input.strip():
            st.sidebar.error("카테고리를 입력해 주세요.")
        elif amount_input <= 0:
            st.sidebar.error("금액을 0원 이상 입력해 주세요.")
        else:
            new_id = (
                st.session_state.df["ID"].max() + 1
                if not st.session_state.df.empty
                else 1
            )
            new_data = pd.DataFrame(
                [
                    {
                        "ID": new_id,
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

# --- [내역 수정] ---
elif action == "✏️ 내역 수정":
    st.sidebar.subheader("기존 내역 수정")
    if not st.session_state.df.empty:
        edit_options = st.session_state.df.apply(
            lambda r: f"[{r['ID']}] {r['날짜']} | {r['유형']} | {r['카테고리']} | {r['금액']:,}원 ({r['내역']})",
            axis=1,
        ).tolist()
        selected_option = st.sidebar.selectbox("수정할 내역 선택", edit_options)
        selected_id = int(selected_option.split("]")[0].replace("[", ""))

        target_row = st.session_state.df[
            st.session_state.df["ID"] == selected_id
        ].iloc[0]

        with st.sidebar.form("edit_form"):
            edit_date = st.date_input("날짜", target_row["날짜"])
            edit_type = st.radio(
                "유형",
                ["지출", "수입"],
                index=0 if target_row["유형"] == "지출" else 1,
                horizontal=True,
            )
            edit_category = st.text_input("카테고리", target_row["카테고리"])
            edit_amount = st.number_input(
                "금액 (원)", min_value=0, step=1000, value=int(target_row["금액"])
            )
            edit_memo = st.text_input("사유 및 상세 내역", target_row["내역"])
            update_button = st.form_submit_button("수정 완료")

        if update_button:
            idx = st.session_state.df[st.session_state.df["ID"] == selected_id].index[0]
            st.session_state.df.loc[idx, "날짜"] = edit_date
            st.session_state.df.loc[idx, "유형"] = edit_type
            st.session_state.df.loc[idx, "카테고리"] = edit_category.strip()
            st.session_state.df.loc[idx, "금액"] = edit_amount
            st.session_state.df.loc[idx, "내역"] = edit_memo
            st.sidebar.success("수정되었습니다!")
            st.rerun()
    else:
        st.sidebar.info("수정할 내역이 없습니다.")

# --- [내역 삭제] ---
elif action == "🗑️ 내역 삭제":
    st.sidebar.subheader("기존 내역 삭제")
    if not st.session_state.df.empty:
        delete_options = st.session_state.df.apply(
            lambda r: f"[{r['ID']}] {r['날짜']} | {r['유형']} | {r['카테고리']} | {r['금액']:,}원 ({r['내역']})",
            axis=1,
        ).tolist()
        selected_option = st.sidebar.selectbox("삭제할 내역 선택", delete_options)
        selected_id = int(selected_option.split("]")[0].replace("[", ""))

        if st.sidebar.button("🗑️ 해당 항목 삭제하기", type="primary"):
            st.session_state.df = st.session_state.df[
                st.session_state.df["ID"] != selected_id
            ].reset_index(drop=True)
            st.sidebar.success("삭제되었습니다!")
            st.rerun()
    else:
        st.sidebar.info("삭제할 내역이 없습니다.")

# -----------------------------------------------------------------------------
# 3. 메인 화면: 탭 구성
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(
    ["📋 전체 내역 목록", "📊 수입/지출 분석 차트", "📅 이달의 요약 & 캘린더"]
)

# -----------------------------------------------------------------------------
# [TAB 1] 전체 내역 목록
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("전체 거래 내역")

    total_income = st.session_state.df[
        st.session_state.df["유형"] == "수입"
    ]["금액"].sum()
    total_expense = st.session_state.df[
        st.session_state.df["유형"] == "지출"
    ]["금액"].sum()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("총 수입", f"{total_income:,} 원")
    col2.metric("총 지출", f"{total_expense:,} 원")
    col3.metric("현재 잔액", f"{balance:,} 원")

    st.divider()

    sorted_df = st.session_state.df.sort_values(
        by="날짜", ascending=False
    ).reset_index(drop=True)

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
# [TAB 2] 수입/지출 분석 차트
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("수입 및 지출 분석")

    if not st.session_state.df.empty:
        col_chart1, col_chart2 = st.columns(2)

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
# [TAB 3] 이달의 요약 & 예쁜 월별 캘린더 (디자인 개선)
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📅 이달의 수입/지출 요약 & 월별 캘린더")

    today = datetime.date.today()

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        selected_year = st.number_input("연도 선택", value=today.year, step=1)
    with col_sel2:
        selected_month = st.number_input("월 선택", min_value=1, max_value=12, value=today.month, step=1)

    df_copy = st.session_state.df.copy()
    df_copy["날짜"] = pd.to_datetime(df_copy["날짜"])

    month_mask = (df_copy["날짜"].dt.year == selected_year) & (
        df_copy["날짜"].dt.month == selected_month
    )
    this_month_df = st.session_state.df.loc[month_mask]

    # --- 1. 요약 정보 ---
    st.divider()
    if not this_month_df.empty:
        m_income = this_month_df[this_month_df["유형"] == "수입"]["금액"].sum()
        m_expense = this_month_df[this_month_df["유형"] == "지출"]["금액"].sum()

        col_m1, col_m2 = st.columns(2)
        col_m1.metric(f"🔵 {selected_month}월 누적 수입", f"{m_income:,} 원")
        col_m2.metric(f"🔴 {selected_month}월 누적 지출", f"{m_expense:,} 원")

        col_top1, col_top2 = st.columns(2)

        with col_top1:
            m_expense_df = this_month_df[this_month_df["유형"] == "지출"]
            if not m_expense_df.empty:
                top_cat_exp = m_expense_df.groupby("카테고리")["금액"].sum().idxmax()
                top_cat_exp_amt = m_expense_df.groupby("카테고리")["금액"].sum().max()
                max_exp_row = m_expense_df.loc[m_expense_df["금액"].idxmax()]

                st.error(
                    f"**🔴 최다 지출 카테고리:** {top_cat_exp} ({top_cat_exp_amt:,}원)\n\n"
                    f"**🔴 최대 단일 지출:** {max_exp_row['내역']} ({max_exp_row['금액']:,}원)"
                )

        with col_top2:
            m_income_df = this_month_df[this_month_df["유형"] == "수입"]
            if not m_income_df.empty:
                top_cat_inc = m_income_df.groupby("카테고리")["금액"].sum().idxmax()
                top_cat_inc_amt = m_income_df.groupby("카테고리")["금액"].sum().max()
                max_inc_row = m_income_df.loc[m_income_df["금액"].idxmax()]

                st.info(
                    f"**🔵 최다 수입 카테고리:** {top_cat_inc} ({top_cat_inc_amt:,}원)\n\n"
                    f"**🔵 최대 단일 수입:** {max_inc_row['내역']} ({max_inc_row['금액']:,}원)"
                )
    else:
        st.info("선택한 달에 기록된 내역이 없습니다.")

    # --- 2. 깔끔한 디자인의 캘린더 UI ---
    st.divider()
    st.subheader(f"🗓️ {selected_year}년 {selected_month}월 캘린더")

    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = cal.monthdayscalendar(selected_year, selected_month)

    # 일별 금액 집계
    daily_summary = {}
    for day in range(1, 32):
        d_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
        d_df = this_month_df[this_month_df["날짜"].astype(str) == d_str]
        inc = d_df[d_df["유형"] == "수입"]["금액"].sum()
        exp = d_df[d_df["유형"] == "지출"]["금액"].sum()
        if inc > 0 or exp > 0:
            daily_summary[day] = {"수입": inc, "지출": exp}

    # Custom CSS 스타일 적용
    st.markdown(
        """
        <style>
        .calendar-header {
            text-align: center;
            font-weight: bold;
            padding: 8px 0;
            background-color: #f7f9fa;
            border-radius: 6px;
            margin-bottom: 8px;
        }
        .sun-header { color: #E53E3E; }
        .sat-header { color: #3182CE; }
        .calendar-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px;
            min-height: 110px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 8px;
        }
        .today-badge {
            background-color: #3182CE;
            color: white;
            border-radius: 50%;
            padding: 2px 7px;
            font-size: 0.85rem;
        }
        .income-badge {
            color: #3182CE;
            background-color: #EBF8FF;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.82rem;
            display: inline-block;
            margin-top: 4px;
        }
        .expense-badge {
            color: #E53E3E;
            background-color: #FFF5F5;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.82rem;
            display: inline-block;
            margin-top: 4px;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # 요일 헤더
    days_header = [("일", "sun-header"), ("월", ""), ("화", ""), ("수", ""), ("목", ""), ("금", ""), ("토", "sat-header")]
    cols = st.columns(7)
    for idx, (d_name, d_class) in enumerate(days_header):
        cols[idx].markdown(
            f"<div class='calendar-header {d_class}'>{d_name}</div>",
            unsafe_allow_html=True,
        )

    # 주별 날짜 출력
    for week in month_days:
        cols = st.columns(7)
        for idx, day in enumerate(week):
            if day == 0:
                cols[idx].write("")
            else:
                is_today = (
                    selected_year == today.year
                    and selected_month == today.month
                    and day == today.day
                )
                
                day_html = f"<span class='today-badge'>{day}</span>" if is_today else f"<b>{day}</b>"
                
                card_html = f"<div class='calendar-card'>{day_html}<br>"

                if day in daily_summary:
                    inc = daily_summary[day]["수입"]
                    exp = daily_summary[day]["지출"]

                    if inc > 0:
                        card_html += f"<div class='income-badge'>+ {inc:,}원</div><br>"
                    if exp > 0:
                        card_html += f"<div class='expense-badge'>- {exp:,}원</div><br>"

                card_html += "</div>"
                cols[idx].markdown(card_html, unsafe_allow_html=True)
