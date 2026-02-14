import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PRIMARY_COLOR = "#2596be"
CHURNED_COLOR = "#FF6B6B"
STAYED_COLOR = "#51CF66"
JOINED_COLOR = "#4DABF7"


@st.cache_data
def load_data(csv_file: str) -> pd.DataFrame:
    df = pd.read_csv(csv_file)
    return df


class Data:
    def __init__(self, csv_file):
        self.df = load_data(csv_file)
        self.filtered_df = self.df.copy()

        self.filters = {
            "State": None,
            "Age": None,
            "Contract": None,
            "Gender": None,
            "Internet_Type": None,
        }

    def set_filters(self, **kwargs):
        self.filters.update(kwargs)
        self.apply_filters()

    def apply_filters(self):
        df = self.df.copy()

        states = self.filters.get("State")
        if states and len(states) > 0:
            df = df[df["State"].isin(states)]

        age_range = self.filters.get("Age")
        if age_range:
            df = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]

        for column in ["Contract", "Gender", "Internet_Type"]:
            values = self.filters.get(column)
            if values and len(values) > 0:
                df = df[df[column].isin(values)]

        self.filtered_df = df

    def unique_values(self, column):
        return sorted(self.df[column].dropna().unique())

    def compute_kpis(self):
        df = self.filtered_df
        total_customers = len(df)
        churned_customers = len(df[df['Customer_Status'] == 'Churned'])
        stayed_customers = len(df[df['Customer_Status'] == 'Stayed'])
        joined_customers = len(df[df['Customer_Status'] == 'Joined'])
        churn_rate = (churned_customers / total_customers) * 100
        avg_revenue = df['Total_Revenue'].mean()
        avg_monthly_charge = df['Monthly_Charge'].mean()
        avg_tenure = df['Tenure_in_Months'].mean()

        return total_customers, churned_customers, stayed_customers, joined_customers, churn_rate, avg_revenue, avg_monthly_charge, avg_tenure


def get_title_style():
    theme = st.get_option("theme.base") or "light"

    return {
        'font': {
            'size': 22,
            'color': 'white' if theme != "dark" else "#2d3748"
        }
    }


class Chart(Data):
    def __init__(self, csv_file: str, theme: str = "plotly"):
        super().__init__(csv_file)
        self.theme = theme

    def chart_customer_status_distribution(self):
        status_counts = self.filtered_df['Customer_Status'].value_counts()

        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            hole=0.4,
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Customer Status Distribution", **get_title_style()},
            height=500
        )

        return fig

    def chart_churn_category_breakdown(self):
        churned_df = self.filtered_df[self.filtered_df['Customer_Status'] == 'Churned']
        churn_category = churned_df['Churn_Category'].value_counts(
        ).sort_values()

        fig = px.bar(
            x=churn_category.values,
            y=churn_category.index,
            orientation='h',
            color=churn_category.values,
            color_continuous_scale='Reds',
            labels={'x': 'Count', 'y': 'Category'}
        )

        fig.update_layout(
            title={'text': "Churn Category Breakdown", **get_title_style()},
            xaxis_title="Count",
            yaxis_title="Category",
            showlegend=False,
            height=500
        )

        return fig

    def chart_top_churn_reasons(self):
        churned_df = self.filtered_df[self.filtered_df['Customer_Status'] == 'Churned']
        churn_reasons = churned_df['Churn_Reason'].value_counts().head(
            10).sort_values()

        # Map reasons to categories for coloring
        reason_to_category = churned_df.groupby(
            'Churn_Reason')['Churn_Category'].first()
        colors = [reason_to_category.get(reason, 'Other')
                  for reason in churn_reasons.index]

        color_map = {
            'Competitor': '#e74c3c',
            'Attitude': '#e67e22',
            'Dissatisfaction': '#f39c12',
            'Price': '#9b59b6',
            'Other': '#95a5a6'
        }

        bar_colors = [color_map.get(cat, '#95a5a6') for cat in colors]

        fig = go.Figure(data=[
            go.Bar(
                x=churn_reasons.values,
                y=churn_reasons.index,
                orientation='h',
                marker=dict(color=bar_colors),
                text=churn_reasons.values,
                textposition='auto'
            )
        ])

        fig.update_layout(
            title={'text': "Top 10 Churn Reasons", **get_title_style()},
            xaxis_title="Count",
            yaxis_title="Churn Reason",
            height=500
        )

        return fig

    def chart_churn_by_tenure(self):
        churned_df = self.filtered_df[self.filtered_df['Customer_Status'] == 'Churned']
        tenure_churn = churned_df.groupby(
            'Tenure_in_Months').size().reset_index(name='Count')

        fig = px.area(
            tenure_churn,
            x='Tenure_in_Months',
            y='Count',
            color_discrete_sequence=[PRIMARY_COLOR]
        )

        # Add average tenure line
        avg_tenure = self.filtered_df['Tenure_in_Months'].mean()
        fig.add_vline(
            x=avg_tenure,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Avg Tenure: {avg_tenure:.1f}",
            annotation_position="top"
        )

        fig.update_layout(
            title={
                'text': "Churn Trend by Tenure (Months)", **get_title_style()},
            xaxis_title="Tenure in Months",
            yaxis_title="Number of Churned Customers",
            height=500
        )

        return fig

    def chart_churn_by_age_group(self):
        bins = [18, 25, 35, 45, 55, 65, 100]
        labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '66+']
        df_copy = self.filtered_df.copy()
        df_copy['Age_Group'] = pd.cut(
            df_copy['Age'], bins=bins, labels=labels, right=False)

        # Group by age group and status
        age_status = df_copy.groupby(
            ['Age_Group', 'Customer_Status'],  observed=True).size().rename('Count').reset_index()
        age_status = age_status[age_status['Customer_Status'].isin(
            ['Churned', 'Stayed'])]

        fig = px.bar(
            age_status,
            x='Age_Group',
            y='Count',
            color='Customer_Status',
            barmode='group',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Churn Rate by Age Group", **get_title_style()},
            xaxis_title="Age Group",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_churn_by_gender(self):
        gender_status = self.filtered_df.groupby(
            ['Gender', 'Customer_Status']).size().reset_index(name='Count')
        gender_status = gender_status[gender_status['Customer_Status'].isin(
            ['Churned', 'Stayed'])]

        fig = px.bar(
            gender_status,
            x='Gender',
            y='Count',
            color='Customer_Status',
            barmode='group',
            text='Count',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Churn by Gender", **get_title_style()},
            xaxis_title="Gender",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_churn_by_marital_status(self):
        marital_status = self.filtered_df.groupby(
            ['Married', 'Customer_Status']).size().reset_index(name='Count')
        marital_status = marital_status[marital_status['Customer_Status'].isin([
                                                                               'Churned', 'Stayed'])]

        fig = px.bar(
            marital_status,
            x='Married',
            y='Count',
            color='Customer_Status',
            barmode='group',
            text='Count',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Churn by Marital Status", **get_title_style()},
            xaxis_title="Marital Status",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_top_states_churn(self):
        churned_df = self.filtered_df[self.filtered_df['Customer_Status'] == 'Churned']
        state_churn = churned_df['State'].value_counts().head(10).sort_values()

        fig = px.bar(
            x=state_churn.values,
            y=state_churn.index,
            orientation='h',
            color=state_churn.values,
            color_continuous_scale='Reds'
        )

        fig.update_layout(
            title={'text': "Top 10 States by Churn Count", **get_title_style()},
            xaxis_title="Churned Customers",
            yaxis_title="State",
            showlegend=False,
            height=450
        )

        return fig

    def chart_age_vs_tenure_scatter(self):
        fig = px.scatter(
            self.filtered_df,
            x='Age',
            y='Tenure_in_Months',
            color='Customer_Status',
            size='Total_Revenue',
            hover_data=['Monthly_Charge', 'Total_Revenue'],
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            },
            opacity=0.6
        )

        fig.update_layout(
            title={'text': "Age vs Tenure Analysis", **get_title_style()},
            xaxis_title="Age",
            yaxis_title="Tenure (Months)",
            height=500
        )

        return fig

    def chart_churn_by_contract_type(self):
        contract_status = self.filtered_df.groupby(
            ['Contract', 'Customer_Status']).size().reset_index(name='Count')
        contract_status = contract_status[contract_status['Customer_Status'].isin([
                                                                                  'Churned', 'Stayed'])]

        fig = px.bar(
            contract_status,
            x='Contract',
            y='Count',
            color='Customer_Status',
            barmode='group',
            text='Count',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Churn Rate by Contract Type", **get_title_style()},
            xaxis_title="Contract Type",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_churn_by_internet_type(self):
        internet_df = self.filtered_df[self.filtered_df['Internet_Type'].notna(
        )]
        internet_status = internet_df.groupby(
            ['Internet_Type', 'Customer_Status']).size().reset_index(name='Count')

        fig = px.bar(
            internet_status,
            x='Internet_Type',
            y='Count',
            color='Customer_Status',
            barmode='stack',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Churn Rate by Internet Type", **get_title_style()},
            xaxis_title="Internet Type",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_service_adoption_heatmap(self):
        services = [
            'Phone_Service', 'Multiple_Lines', 'Online_Security', 'Online_Backup',
            'Device_Protection_Plan', 'Premium_Support', 'Streaming_TV',
            'Streaming_Movies', 'Streaming_Music', 'Unlimited_Data'
        ]

        # Calculate percentage of "Yes" for each service by status
        heatmap_data = []
        statuses = ['Stayed', 'Churned']

        for status in statuses:
            status_df = self.filtered_df[self.filtered_df['Customer_Status'] == status]
            percentages = []
            for service in services:
                if service in status_df.columns:
                    pct = (status_df[service] == 'Yes').sum() / \
                        len(status_df) * 100
                    percentages.append(pct)
                else:
                    percentages.append(0)
            heatmap_data.append(percentages)

        # Clean service names
        service_labels = [s.replace('_', ' ').title() for s in services]

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=service_labels,
            y=statuses,
            colorscale='Blues',
            text=[[f'{val:.1f}%' for val in row] for row in heatmap_data],
            texttemplate='%{text}',
            textfont={"size": 10}
        ))

        fig.update_layout(
            title={
                'text': "Service Adoption Heatmap (% of Customers)", **get_title_style()},
            xaxis_title="Services",
            yaxis_title="Customer Status",
            height=450
        )

        return fig

    def chart_payment_method_vs_churn(self):
        payment_status = self.filtered_df.groupby(
            ['Payment_Method', 'Customer_Status']).size().reset_index(name='Count')
        payment_status = payment_status[payment_status['Customer_Status'].isin([
                                                                               'Churned', 'Stayed'])]

        fig = px.bar(
            payment_status,
            x='Payment_Method',
            y='Count',
            color='Customer_Status',
            barmode='group',
            text='Count',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Payment Method vs Churn", **get_title_style()},
            xaxis_title="Payment Method",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_paperless_billing_impact(self):
        paperless_churn = self.filtered_df.groupby(
            ['Paperless_Billing', 'Customer_Status']).size().reset_index(name='Count')
        paperless_churn = paperless_churn[paperless_churn['Customer_Status'] == 'Churned']

        fig = px.pie(
            paperless_churn,
            values='Count',
            names='Paperless_Billing',
            hole=0.4,
            color_discrete_sequence=[CHURNED_COLOR, '#FF9999']
        )

        fig.update_layout(
            title={'text': "Paperless Billing Impact on Churn",
                   **get_title_style()},
            height=450
        )

        return fig

    def chart_revenue_lost_to_churn(self):
        churned_df = self.filtered_df[self.filtered_df['Customer_Status'] == 'Churned']
        total_lost = churned_df['Total_Revenue'].sum()

        # Revenue by churn category
        revenue_by_category = churned_df.groupby(
            'Churn_Category')['Total_Revenue'].sum().sort_values(ascending=False)

        fig = px.bar(
            x=revenue_by_category.index,
            y=revenue_by_category.values,
            color=revenue_by_category.values,
            color_continuous_scale='Reds',
            text=[f'${val:,.0f}' for val in revenue_by_category.values]
        )

        fig.update_layout(
            title={
                'text': f"Revenue Lost to Churn by Category (Total: ${total_lost:,.0f})", **get_title_style()},
            xaxis_title="Churn Category",
            yaxis_title="Total Revenue Lost ($)",
            showlegend=False,
            height=450
        )

        return fig

    def chart_monthly_charge_distribution(self):
        fig = px.histogram(
            self.filtered_df,
            x='Monthly_Charge',
            color='Customer_Status',
            barmode='overlay',
            nbins=30,
            opacity=0.7,
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Monthly Charge Distribution", **get_title_style()},
            xaxis_title="Monthly Charge ($)",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_total_revenue_distribution(self):
        fig = px.box(
            self.filtered_df,
            x='Customer_Status',
            y='Total_Revenue',
            color='Customer_Status',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Total Revenue Distribution by Customer Status",
                   **get_title_style()},
            xaxis_title="Customer Status",
            yaxis_title="Total Revenue ($)",
            showlegend=False,
            height=450
        )

        return fig

    def chart_revenue_by_contract_type(self):
        revenue_contract = self.filtered_df.groupby(['Contract', 'Customer_Status'])[
            'Total_Revenue'].mean().reset_index()
        revenue_contract = revenue_contract[revenue_contract['Customer_Status'].isin([
                                                                                     'Churned', 'Stayed'])]

        fig = px.bar(
            revenue_contract,
            x='Contract',
            y='Total_Revenue',
            color='Customer_Status',
            barmode='group',
            text=[f'${val:,.0f}' for val in revenue_contract['Total_Revenue']],
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Average Revenue by Contract Type",
                   **get_title_style()},
            xaxis_title="Contract Type",
            yaxis_title="Average Total Revenue ($)",
            height=450
        )

        return fig

    def chart_charges_breakdown(self):
        charge_breakdown = self.filtered_df.groupby('Customer_Status').agg({
            'Total_Charges': 'sum',
            'Total_Refunds': 'sum',
            'Total_Extra_Data_Charges': 'sum',
            'Total_Long_Distance_Charges': 'sum'
        }).reset_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='Total Charges',
            x=charge_breakdown['Customer_Status'],
            y=charge_breakdown['Total_Charges'],
            marker_color=PRIMARY_COLOR
        ))

        fig.add_trace(go.Bar(
            name='Refunds',
            x=charge_breakdown['Customer_Status'],
            y=charge_breakdown['Total_Refunds'],
            marker_color='#e74c3c'
        ))

        fig.add_trace(go.Bar(
            name='Extra Data Charges',
            x=charge_breakdown['Customer_Status'],
            y=charge_breakdown['Total_Extra_Data_Charges'],
            marker_color='#f39c12'
        ))

        fig.add_trace(go.Bar(
            name='Long Distance Charges',
            x=charge_breakdown['Customer_Status'],
            y=charge_breakdown['Total_Long_Distance_Charges'],
            marker_color='#9b59b6'
        ))

        fig.update_layout(
            title={'text': "Charges Breakdown by Customer Status",
                   **get_title_style()},
            xaxis_title="Customer Status",
            yaxis_title="Total Amount ($)",
            barmode='stack',
            height=450
        )

        return fig

    def chart_monthly_charge_vs_tenure(self):
        fig = px.scatter(
            self.filtered_df,
            x='Tenure_in_Months',
            y='Monthly_Charge',
            color='Customer_Status',
            trendline='ols',
            opacity=0.6,
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={
                'text': "Monthly Charge vs Tenure (with Trend Lines)", **get_title_style()},
            xaxis_title="Tenure (Months)",
            yaxis_title="Monthly Charge ($)",
            height=500
        )

        return fig

    def chart_churn_by_referrals(self):
        referral_churn = self.filtered_df.groupby('Number_of_Referrals').agg({
            'Customer_ID': 'count',
            'Customer_Status': lambda x: (x == 'Churned').sum()
        }).reset_index()

        referral_churn.columns = ['Number_of_Referrals', 'Total', 'Churned']
        referral_churn['Churn_Rate'] = (
            referral_churn['Churned'] / referral_churn['Total']) * 100

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=referral_churn['Number_of_Referrals'],
            y=referral_churn['Churn_Rate'],
            mode='lines+markers',
            name='Churn Rate',
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title={'text': "Churn Rate by Number of Referrals",
                   **get_title_style()},
            xaxis_title="Number of Referrals",
            yaxis_title="Churn Rate (%)",
            height=450
        )

        return fig

    def chart_referral_distribution(self):
        fig = px.histogram(
            self.filtered_df,
            x='Number_of_Referrals',
            color='Customer_Status',
            barmode='overlay',
            opacity=0.7,
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Referral Distribution by Customer Status",
                   **get_title_style()},
            xaxis_title="Number of Referrals",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_avg_referrals_by_status(self):
        avg_referrals = self.filtered_df.groupby('Customer_Status')[
            'Number_of_Referrals'].mean().reset_index()
        avg_referrals.columns = ['Customer_Status', 'Avg_Referrals']

        colors = [STAYED_COLOR if status == 'Stayed' else CHURNED_COLOR if status == 'Churned' else JOINED_COLOR
                  for status in avg_referrals['Customer_Status']]

        fig = px.bar(
            avg_referrals,
            x='Customer_Status',
            y='Avg_Referrals',
            text=[f'{val:.2f}' for val in avg_referrals['Avg_Referrals']],
            color='Customer_Status',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Average Referrals by Customer Status",
                   **get_title_style()},
            xaxis_title="Customer Status",
            yaxis_title="Average Number of Referrals",
            showlegend=False,
            height=450
        )

        return fig

    def chart_value_deal_impact(self):
        # Fill NaN with 'No Deal'
        df_copy = self.filtered_df.copy()
        df_copy['Value_Deal'] = df_copy['Value_Deal'].fillna('No Deal')

        deal_status = df_copy.groupby(
            ['Value_Deal', 'Customer_Status']).size().reset_index(name='Count')
        deal_status = deal_status[deal_status['Customer_Status'].isin(
            ['Churned', 'Stayed'])]

        fig = px.bar(
            deal_status,
            x='Value_Deal',
            y='Count',
            color='Customer_Status',
            barmode='group',
            text='Count',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Value Deal Impact on Customer Status",
                   **get_title_style()},
            xaxis_title="Value Deal Type",
            yaxis_title="Count",
            height=450
        )

        return fig

    def chart_correlation_heatmap(self):
        # Select numeric columns
        numeric_cols = ['Age', 'Tenure_in_Months',
                        'Monthly_Charge', 'Total_Revenue', 'Number_of_Referrals']

        # Create a binary churn column
        df_copy = self.filtered_df[self.filtered_df['Customer_Status'].isin(
            ['Churned', 'Stayed'])].copy()
        df_copy['Churned'] = (df_copy['Customer_Status']
                              == 'Churned').astype(int)

        # Calculate correlation with churn
        correlations = df_copy[numeric_cols +
                               ['Churned']].corr()['Churned'].drop('Churned')

        # Create correlation matrix for all variables
        corr_matrix = df_copy[numeric_cols].corr()

        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))

        fig.update_layout(
            title={'text': "Feature Correlation Heatmap", **get_title_style()},
            height=500
        )

        return fig

    def chart_tenure_vs_churn_rate(self):
        # Create tenure buckets
        bins = [0, 6, 12, 18, 24, 30, 36]
        labels = ['0-6', '7-12', '13-18', '19-24', '25-30', '31-36']
        df_copy = self.filtered_df.copy()
        df_copy['Tenure_Bucket'] = pd.cut(
            df_copy['Tenure_in_Months'], bins=bins, labels=labels, include_lowest=True)

        # Calculate churn rate per bucket
        tenure_churn = df_copy.groupby('Tenure_Bucket', observed=True).agg({
            'Customer_ID': 'count',
            'Customer_Status': lambda x: (x == 'Churned').sum()
        }).reset_index()

        tenure_churn.columns = ['Tenure_Bucket', 'Total', 'Churned']
        tenure_churn['Churn_Rate'] = (
            tenure_churn['Churned'] / tenure_churn['Total']) * 100

        fig = px.line(
            tenure_churn,
            x='Tenure_Bucket',
            y='Churn_Rate',
            markers=True,
            line_shape='spline'
        )

        fig.update_traces(line_color=PRIMARY_COLOR,
                          line_width=3, marker_size=10)

        fig.update_layout(
            title={
                'text': "Churn Rate by Tenure Buckets (Months)", **get_title_style()},
            xaxis_title="Tenure Bucket (Months)",
            yaxis_title="Churn Rate (%)",
            height=450
        )

        return fig

    def chart_service_count_vs_churn(self):
        # Count services for each customer
        service_cols = [
            'Phone_Service', 'Multiple_Lines', 'Online_Security', 'Online_Backup',
            'Device_Protection_Plan', 'Premium_Support', 'Streaming_TV',
            'Streaming_Movies', 'Streaming_Music', 'Unlimited_Data'
        ]

        df_copy = self.filtered_df.copy()
        df_copy['Service_Count'] = df_copy[service_cols].apply(
            lambda x: (x == 'Yes').sum(), axis=1)

        fig = px.violin(
            df_copy[df_copy['Customer_Status'].isin(['Churned', 'Stayed'])],
            x='Customer_Status',
            y='Service_Count',
            color='Customer_Status',
            box=True,
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Service Count Distribution by Customer Status",
                   **get_title_style()},
            xaxis_title="Customer Status",
            yaxis_title="Number of Services",
            showlegend=False,
            height=450
        )

        return fig

    def chart_predictive_risk_segments(self):
        # Create hierarchy: Contract -> Internet Type -> Customer Status
        df_sunburst = self.filtered_df[self.filtered_df['Internet_Type'].notna()].copy(
        )

        fig = px.sunburst(
            df_sunburst,
            path=['Contract', 'Internet_Type', 'Customer_Status'],
            color='Customer_Status',
            color_discrete_map={
                'Stayed': STAYED_COLOR,
                'Churned': CHURNED_COLOR,
                'Joined': JOINED_COLOR
            }
        )

        fig.update_layout(
            title={'text': "Customer Segmentation: Contract → Internet Type → Status",
                   **get_title_style()},
            height=600
        )

        return fig
