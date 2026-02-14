import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .data import load_data

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (20, 12)

PRIMARY_COLOR = "#2596be"
CRITICAL_COLOR = "#FF4B4B"
HIGH_COLOR = "#FFA500"
MEDIUM_COLOR = "#FFD700"
LOW_COLOR = "#51CF66"
DASHBOARD_BG = "#3B4BA0"


class Prediction:
    def __init__(self, all_customer_prediction_file, predicted_churners_file, summary_file):
        self.df_all = load_data(all_customer_prediction_file)
        self.predicted_churners = load_data(predicted_churners_file)
        self.summary = load_data(summary_file)

    @staticmethod
    def churn_type_list():
        return [
            "Combined Dashboard",
            "Chart Total Predicted Churners",
            "Churners by State",
            "Risk Level Distribution",
            "Churners by Age Group",
            "Churners by Gender",
            "Churners by Marital Status",
            "Churners by Contract Type",
            "Churners by Tenure Group",
            "Churners by Payment Method",
            "Average Churn Risk Gauge",
            "Top Risk Factors",
            "Revenue at Risk",
            "Monthly Charge Distribution",
            "High Risk Customers Table"

        ]

    def get_chart(self, section_name):
        mapping = {
            "Chart Total Predicted Churners": self.chart_total_predicted_churners,
            "Churners by State": self.chart_churners_by_state,
            "Risk Level Distribution": self.chart_risk_level_distribution,
            "Churners by Age Group": self.chart_churners_by_age_group,
            "Churners by Gender": self.chart_churners_by_gender,
            "Churners by Marital Status": self.chart_churners_by_marital_status,
            "Churners by Contract Type": self.chart_churners_by_contract_type,
            "Churners by Tenure Group": self.chart_churners_by_tenure_group,
            "Churners by Payment Method": self.chart_churners_by_payment_method,
            "Average Churn Risk Gauge": self.chart_average_churn_risk_gauge,
            "Top Risk Factors": self.chart_top_risk_factors,
            "Revenue at Risk": self.chart_revenue_at_risk,
            "Monthly Charge Distribution": self.chart_monthly_charge_distribution,
            "High Risk Customers Table": self.create_high_risk_customers_table,
            "Combined Dashboard": self.create_combined_dashboard
        }

        if section_name in mapping:
            return mapping[section_name]()

    def chart_total_predicted_churners(self):
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=len(self.predicted_churners),
            title={'text': "PREDICTED CHURNERS", 'font': {'size': 24}},
            number={'font': {'size': 60, 'color': CRITICAL_COLOR}},
            delta={
                'reference': self.summary['predicted_churners'].iloc[0] * 0.8,
                'valueformat': '.0f'
            }
        ))

        fig.update_layout(
            height=300,
            title={
                'text': "Total Predicted Churners",
                'font': {'size': 20, 'color': 'white'}
            }
        )

        return fig

    def chart_churners_by_state(self, top_n=10):
        state_counts = self.predicted_churners['State'].value_counts().head(
            top_n).sort_values()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=state_counts.index,
            x=state_counts.values,
            orientation='h',
            marker_color=PRIMARY_COLOR,
            text=state_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': f"Top {top_n} States by Predicted Churners",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Number of Churners",
            yaxis_title="State",
            height=500
        )

        return fig

    def chart_risk_level_distribution(self):
        risk_counts = self.predicted_churners['Risk_Level'].value_counts()

        colors_risk = {
            'Critical': CRITICAL_COLOR,
            'High': HIGH_COLOR,
            'Medium': MEDIUM_COLOR,
            'Low': LOW_COLOR
        }

        colors = [colors_risk.get(level, PRIMARY_COLOR)
                  for level in risk_counts.index]

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=risk_counts.index,
            values=risk_counts.values,
            marker_colors=colors,
            hole=0.4,
            textinfo='label+value+percent',
            textfont={'size': 14}
        ))

        fig.update_layout(
            title={
                'text': "Risk Level Distribution",
                'font': {'size': 24, 'color': 'white'}
            },
            height=500
        )

        return fig

    def chart_churners_by_age_group(self):
        bins = [0, 30, 40, 50, 60, 100]
        labels = ['<30', '30-40', '40-50', '50-60', '>60']
        predicted_churners_copy = self.predicted_churners.copy()
        predicted_churners_copy['Age_Group'] = pd.cut(
            predicted_churners_copy['Age'],
            bins=bins,
            labels=labels
        )
        age_counts = predicted_churners_copy['Age_Group'].value_counts(
        ).sort_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=age_counts.index,
            y=age_counts.values,
            marker_color=PRIMARY_COLOR,
            text=age_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': "Predicted Churners by Age Group",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Age Group",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_churners_by_gender(self):
        gender_counts = self.predicted_churners['Gender'].value_counts()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=gender_counts.index,
            y=gender_counts.values,
            marker_color=[HIGH_COLOR, PRIMARY_COLOR],
            text=gender_counts.values,
            textposition='auto',
            textfont={'size': 40, 'color': 'white'}
        ))

        fig.update_layout(
            title={
                'text': f"Predicted Churners by Gender (Total: {len(self.predicted_churners)})",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Gender",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_churners_by_marital_status(self):
        marital_counts = self.predicted_churners['Married'].value_counts()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=marital_counts.index,
            y=marital_counts.values,
            marker_color=[PRIMARY_COLOR, HIGH_COLOR],
            text=marital_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': "Predicted Churners by Marital Status",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Marital Status",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_churners_by_contract_type(self):
        contract_counts = self.predicted_churners['Contract'].value_counts()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=contract_counts.index,
            y=contract_counts.values,
            marker_color=[CRITICAL_COLOR, HIGH_COLOR, MEDIUM_COLOR],
            text=contract_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': "Predicted Churners by Contract Type",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Contract Type",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_churners_by_tenure_group(self):
        tenure_bins = [0, 6, 12, 24, 36]
        tenure_labels = ['<6', '6-12', '12-24', '24-36']
        predicted_churners_copy = self.predicted_churners.copy()
        predicted_churners_copy['Tenure_Group'] = pd.cut(
            predicted_churners_copy['Tenure_in_Months'],
            bins=tenure_bins,
            labels=tenure_labels
        )
        tenure_counts = predicted_churners_copy['Tenure_Group'].value_counts(
        ).sort_index()

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=tenure_counts.index,
            y=tenure_counts.values,
            marker_color=PRIMARY_COLOR,
            text=tenure_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': "Predicted Churners by Tenure Group (Months)",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Tenure Group",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_churners_by_payment_method(self):
        payment_counts = self.predicted_churners['Payment_Method'].value_counts(
        )

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=payment_counts.index,
            y=payment_counts.values,
            marker_color=[PRIMARY_COLOR, HIGH_COLOR, MEDIUM_COLOR],
            text=payment_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': "Predicted Churners by Payment Method",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Payment Method",
            yaxis_title="Number of Churners",
            height=450
        )

        return fig

    def chart_average_churn_risk_gauge(self):
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=self.chart_average_churn_risk_gaugesummary['avg_churn_probability'].iloc[0] * 100,
            title={'text': "Average Churn Risk %", 'font': {'size': 20}},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': CRITICAL_COLOR},
                'steps': [
                    {'range': [0, 30], 'color': LOW_COLOR},
                    {'range': [30, 50], 'color': MEDIUM_COLOR},
                    {'range': [50, 70], 'color': HIGH_COLOR},
                    {'range': [70, 100], 'color': CRITICAL_COLOR}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))

        fig.update_layout(
            title={
                'text': "Model Performance - Average Risk",
                'font': {'size': 24, 'color': 'white'}
            },
            height=400
        )

        return fig

    def chart_top_risk_factors(self, top_n=8):
        all_factors = []
        for factors in self.predicted_churners['Top_Risk_Factors'].dropna():
            all_factors.extend([f.strip() for f in factors.split(',')])

        factor_counts = pd.Series(all_factors).value_counts().head(top_n)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=factor_counts.index,
            x=factor_counts.values,
            orientation='h',
            marker_color=CRITICAL_COLOR,
            text=factor_counts.values,
            textposition='auto'
        ))

        fig.update_layout(
            title={
                'text': f"Top {top_n} Risk Factors Driving Churn",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Number of Customers",
            yaxis_title="Risk Factor",
            height=500
        )

        return fig

    def chart_revenue_at_risk(self):
        fig = go.Figure()

        fig.add_trace(go.Indicator(
            mode="number",
            value=self.summary['total_revenue_at_risk'].iloc[0],
            title={'text': "Total Revenue at Risk", 'font': {'size': 20}},
            number={'prefix': "$", 'font': {'size': 50,
                                            'color': CRITICAL_COLOR}, 'valueformat': ',.2f'}
        ))

        fig.update_layout(
            title={
                'text': "Financial Impact",
                'font': {'size': 24, 'color': 'white'}
            },
            height=300
        )

        return fig

    def chart_monthly_charge_distribution(self):
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=self.predicted_churners['Monthly_Charge'],
            nbinsx=20,
            marker_color=PRIMARY_COLOR,
            name='Monthly Charge'
        ))

        fig.update_layout(
            title={
                'text': "Monthly Charge Distribution of Predicted Churners",
                'font': {'size': 24, 'color': 'white'}
            },
            xaxis_title="Monthly Charge ($)",
            yaxis_title="Number of Customers",
            height=450
        )

        return fig

    def create_high_risk_customers_table(self, top_n=20):
        top_customers = self.predicted_churners.nlargest(top_n, 'Churn_Probability')[[
            'Customer_ID', 'Monthly_Charge', 'Total_Revenue', 'Total_Refunds',
            'Number_of_Referrals', 'Tenure_in_Months', 'Churn_Probability',
            'Risk_Level', 'Top_Risk_Factors'
        ]].copy()

        # Round numbers
        top_customers['Monthly_Charge'] = top_customers['Monthly_Charge'].round(
            2)
        top_customers['Total_Revenue'] = top_customers['Total_Revenue'].round(
            2)
        top_customers['Churn_Probability'] = (
            top_customers['Churn_Probability'] * 100).round(1)

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Customer ID</b>', '<b>Monthly Charge</b>', '<b>Total Revenue</b>',
                        '<b>Total Refunds</b>', '<b>Referrals</b>', '<b>Tenure (Months)</b>',
                        '<b>Churn Risk %</b>', '<b>Risk Level</b>', '<b>Top Risk Factors</b>'],
                fill_color=DASHBOARD_BG,
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[
                    top_customers['Customer_ID'],
                    top_customers['Monthly_Charge'],
                    top_customers['Total_Revenue'],
                    top_customers['Total_Refunds'],
                    top_customers['Number_of_Referrals'],
                    top_customers['Tenure_in_Months'],
                    top_customers['Churn_Probability'],
                    top_customers['Risk_Level'],
                    top_customers['Top_Risk_Factors']
                ],
                fill_color='white',
                font=dict(color='black', size=11),
                align='left',
                height=30
            )
        )])

        fig.update_layout(
            title={
                'text': f"Top {top_n} Highest Risk Customers - Priority Action List",
                'font': {'size': 24, 'color': 'white'}
            },
            width=1800,
            height=800
        )

        return fig

    def create_combined_dashboard(self):
        # Create figure with subplots
        fig = make_subplots(
            rows=4, cols=3,
            subplot_titles=(
                'Predicted Churner Count', 'By State (Top 10)', 'Risk Level Distribution',
                'By Age Group', 'By Marital Status', 'By Contract Type',
                'By Tenure Group', 'By Payment Method', 'Avg Churn Risk %',
                'Top Risk Factors', 'Revenue at Risk', 'Monthly Charge Distribution'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'bar'}, {'type': 'pie'}],
                [{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}],
                [{'type': 'bar'}, {'type': 'bar'}, {'type': 'indicator'}],
                [{'type': 'bar'}, {'type': 'indicator'}, {'type': 'histogram'}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.10
        )

        # Row 1, Col 1: Total Predicted Churners
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=len(self.predicted_churners),
                title={'text': "PREDICTED CHURNERS"},
                number={'font': {'size': 50, 'color': CRITICAL_COLOR}},
                delta={
                    'reference': self.summary['predicted_churners'].iloc[0] * 0.8}
            ),
            row=1, col=1
        )

        # Row 1, Col 2: By State
        state_counts = self.predicted_churners['State'].value_counts().head(
            10).sort_values()
        fig.add_trace(
            go.Bar(
                y=state_counts.index,
                x=state_counts.values,
                orientation='h',
                marker_color=PRIMARY_COLOR,
                text=state_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=1, col=2
        )

        # Row 1, Col 3: Risk Level Distribution
        risk_counts = self.predicted_churners['Risk_Level'].value_counts()
        colors_risk = [CRITICAL_COLOR if x == 'Critical' else HIGH_COLOR if x == 'High'
                       else MEDIUM_COLOR if x == 'Medium' else LOW_COLOR
                       for x in risk_counts.index]
        fig.add_trace(
            go.Pie(
                labels=risk_counts.index,
                values=risk_counts.values,
                marker_colors=colors_risk,
                hole=0.4,
                showlegend=False
            ),
            row=1, col=3
        )

        # Row 2, Col 1: By Age Group
        bins = [0, 30, 40, 50, 60, 100]
        labels_age = ['<30', '30-40', '40-50', '50-60', '>60']
        predicted_churners_temp = self.predicted_churners.copy()
        predicted_churners_temp['Age_Group'] = pd.cut(
            predicted_churners_temp['Age'], bins=bins, labels=labels_age)
        age_counts = predicted_churners_temp['Age_Group'].value_counts(
        ).sort_index()
        fig.add_trace(
            go.Bar(
                x=age_counts.index,
                y=age_counts.values,
                marker_color=PRIMARY_COLOR,
                text=age_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=2, col=1
        )

        # Row 2, Col 2: By Marital Status
        marital_counts = self.predicted_churners['Married'].value_counts()
        fig.add_trace(
            go.Bar(
                x=marital_counts.index,
                y=marital_counts.values,
                marker_color=[PRIMARY_COLOR, HIGH_COLOR],
                text=marital_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=2, col=2
        )

        # Row 2, Col 3: By Contract Type
        contract_counts = self.predicted_churners['Contract'].value_counts()
        fig.add_trace(
            go.Bar(
                x=contract_counts.index,
                y=contract_counts.values,
                marker_color=[CRITICAL_COLOR, HIGH_COLOR, MEDIUM_COLOR],
                text=contract_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=2, col=3
        )

        # Row 3, Col 1: By Tenure Group
        tenure_bins = [0, 6, 12, 24, 36]
        tenure_labels = ['<6', '6-12', '12-24', '24-36']
        predicted_churners_temp['Tenure_Group'] = pd.cut(
            predicted_churners_temp['Tenure_in_Months'],
            bins=tenure_bins,
            labels=tenure_labels
        )
        tenure_counts = predicted_churners_temp['Tenure_Group'].value_counts(
        ).sort_index()
        fig.add_trace(
            go.Bar(
                x=tenure_counts.index,
                y=tenure_counts.values,
                marker_color=PRIMARY_COLOR,
                text=tenure_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=3, col=1
        )

        # Row 3, Col 2: By Payment Method
        payment_counts = self.predicted_churners['Payment_Method'].value_counts(
        )
        fig.add_trace(
            go.Bar(
                x=payment_counts.index,
                y=payment_counts.values,
                marker_color=[PRIMARY_COLOR, HIGH_COLOR, MEDIUM_COLOR],
                text=payment_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=3, col=2
        )

        # Row 3, Col 3: Average Churn Risk Gauge
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=self.summary['avg_churn_probability'].iloc[0] * 100,
                title={'text': "Avg Risk %"},
                number={'suffix': "%"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': CRITICAL_COLOR},
                    'steps': [
                        {'range': [0, 30], 'color': LOW_COLOR},
                        {'range': [30, 50], 'color': MEDIUM_COLOR},
                        {'range': [50, 70], 'color': HIGH_COLOR},
                        {'range': [70, 100], 'color': CRITICAL_COLOR}
                    ]
                }
            ),
            row=3, col=3
        )

        # Row 4, Col 1: Top Risk Factors
        all_factors = []
        for factors in self.predicted_churners['Top_Risk_Factors'].dropna():
            all_factors.extend([f.strip() for f in factors.split(',')])
        factor_counts = pd.Series(all_factors).value_counts().head(8)
        fig.add_trace(
            go.Bar(
                y=factor_counts.index,
                x=factor_counts.values,
                orientation='h',
                marker_color=CRITICAL_COLOR,
                text=factor_counts.values,
                textposition='auto',
                showlegend=False
            ),
            row=4, col=1
        )

        # Row 4, Col 2: Revenue at Risk
        fig.add_trace(
            go.Indicator(
                mode="number",
                value=self.summary['total_revenue_at_risk'].iloc[0],
                title={'text': "Revenue at Risk"},
                number={'prefix': "$", 'font': {
                    'size': 35, 'color': CRITICAL_COLOR}}
            ),
            row=4, col=2
        )

        # Row 4, Col 3: Monthly Charge Distribution
        fig.add_trace(
            go.Histogram(
                x=self.predicted_churners['Monthly_Charge'],
                nbinsx=20,
                marker_color=PRIMARY_COLOR,
                showlegend=False
            ),
            row=4, col=3
        )

        # Update layout
        fig.update_layout(
            height=1600,
            width=1800,
            title_text="🎯 CHURN PREDICTION DASHBOARD - PREDICTED CHURNERS PROFILE",
            title_font_size=28,
            showlegend=False,
            template='plotly_white'
        )

        return fig
