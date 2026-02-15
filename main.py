import streamlit as st
from components import Chart, Prediction

st.set_page_config(
    page_title="Customer Churn Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    f"""
    <style>
        :root {{
            --primary-color: {"#2596be"};
        }}
        div[data-testid="stMetric"] {{
            border-left: 0.5rem solid #2596be !important;
            box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
            padding: 0 0 0 2% !important;
            border-radius: 12px !important;
            background-color: transparent !important;
        }}
        div[data-testid="stMetric"] label{{
            margin-bottom: 5px;
        }}

        #customer-churn-analysis-dashboard{{
            margin-bottom:15px;
         }}

        /* Reduce top padding */
        .block-container {{
            padding-top: 2rem;
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            margin-top: 32px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            padding: 10px 20px;
            background-color: transparent;
            border-radius: 5px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: var(--primary-color);
            color: white;
        }}

        .st-bq{{
            background-color: #2596be;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title('📊 Customer Churn Analysis Dashboard')
c = Chart('data/churn.csv')
prediction = Prediction('data/all_customers_predictions.csv',
                        'data/predicted_churners.csv', 'data/prediction_summary.csv')
with st.sidebar:
    st.header("🔍 Filters")
    states = sorted(c.df['State'].dropna().unique().tolist())
    state = st.sidebar.multiselect("Select State(s)", states, default=states)

    age_df = c.df['Age']
    age_range = st.sidebar.slider(
        "Age Range",
        min_value=int(age_df.min()),
        max_value=int(age_df.max()),
        value=(int(age_df.min()), int(age_df.max()))
    )

    contract_types = c.unique_values('Contract')
    selected_contract = st.sidebar.multiselect(
        "Contract Type", contract_types, default=contract_types)

    genders = c.unique_values('Gender')
    selected_gender = st.sidebar.multiselect(
        "Gender", genders, default=genders)

    internet_types = c.unique_values('Internet_Type')
    selected_internet = st.sidebar.multiselect(
        "Internet Type", internet_types, default=internet_types)


c.set_filters(
    State=state,
    Age=age_range,
    Contract=selected_contract,
    Gender=selected_gender,
    Internet_Type=selected_internet
)

total_customers, churned_customers, stayed_customers, joined_customers, churn_rate, avg_revenue, avg_monthly_charge, avg_tenure = c.compute_kpis()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="👥 Total Customers",
        value=f"{total_customers:,}"
    )

with col2:
    st.metric(
        label="📉 Churn Rate",
        value=f"{churn_rate:.2f}%",
        delta=f"-{churn_rate:.2f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="❌ Churned Customers",
        value=f"{churned_customers:,}"
    )

with col4:
    st.metric(
        label="✅ Active Customers",
        value=f"{stayed_customers:,}"
    )

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.metric(
        label="💰 Avg Revenue per Customer",
        value=f"${avg_revenue:,.2f}"
    )

with col6:
    st.metric(
        label="💳 Avg Monthly Charge",
        value=f"${avg_monthly_charge:.2f}"
    )

with col7:
    st.metric(
        label="⏱️ Avg Customer Tenure",
        value=f"{avg_tenure:.1f} months"
    )

with col8:
    st.metric(
        label="🆕 New Customers",
        value=f"{joined_customers:,}"
    )


tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Overview & Churn Summary",
    "👥 Customer Demographics",
    "📋 Service & Contract Analysis",
    "💵 Revenue & Financial Analysis",
    "🎯 Referral & Engagement",
    "🔍 Advanced Insights",
    "🤖 Churn Prediction"
])


with tab1:
    st.markdown("### Overview & Churn Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.chart_customer_status_distribution(),
                        width='stretch')
    with col2:
        st.plotly_chart(c.chart_churn_category_breakdown(), width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(c.chart_top_churn_reasons(), width='stretch')

    with col4:
        st.plotly_chart(c.chart_churn_by_tenure(), width='stretch')

with tab2:
    st.markdown("### Customer Demographics Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(c.chart_churn_by_age_group(), width='stretch')

    with col2:
        st.plotly_chart(c.chart_churn_by_gender(), width='stretch')

    col3, col4 = st.columns(2)

    with col3:
        st.plotly_chart(c.chart_churn_by_marital_status(), width='stretch')

    with col4:
        st.plotly_chart(c.chart_top_states_churn(), width='stretch')

    st.plotly_chart(c.chart_age_vs_tenure_scatter(), width='stretch')

with tab3:
    st.markdown("### Service & Contract Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.chart_churn_by_contract_type(), width='stretch')
    with col2:
        st.plotly_chart(c.chart_churn_by_internet_type(), width='stretch')

    st.plotly_chart(c.chart_service_adoption_heatmap(), width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(c.chart_payment_method_vs_churn(), width='stretch')

    with col4:
        st.plotly_chart(c.chart_paperless_billing_impact(), width='stretch')

with tab4:
    st.markdown("### Revenue & Financial Analysis")

    st.plotly_chart(c.chart_revenue_lost_to_churn(), width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.chart_monthly_charge_distribution(),
                        width='stretch')

    with col2:
        st.plotly_chart(c.chart_total_revenue_distribution(),
                        width='stretch')

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(c.chart_revenue_by_contract_type(),
                        width='stretch')
    with col4:
        st.plotly_chart(c.chart_charges_breakdown(), width='stretch')

    st.plotly_chart(c.chart_monthly_charge_vs_tenure(),
                    width='stretch')

with tab5:
    st.markdown("### Referral & Engagement Analysis")

    st.plotly_chart(c.chart_churn_by_referrals(), width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.chart_referral_distribution(), width='stretch')

    with col2:
        st.plotly_chart(c.chart_avg_referrals_by_status(), width='stretch')

    st.plotly_chart(c.chart_value_deal_impact(), width='stretch')

with tab6:
    st.markdown("### Advanced Insights & Correlations")

    st.plotly_chart(c.chart_correlation_heatmap(), width='stretch')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(c.chart_tenure_vs_churn_rate(), width='stretch')

    with col2:
        st.plotly_chart(c.chart_service_count_vs_churn(), width='stretch')

    st.plotly_chart(c.chart_predictive_risk_segments(), width='stretch')

with tab7:
    st.markdown("### Churn Prediction")

    churn_type = st.selectbox('Churn Type: ', prediction.churn_type_list())
    fig = prediction.get_chart(churn_type)
    st.plotly_chart(fig, width='stretch')
