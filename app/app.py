import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px
import os
import base64
from openai import OpenAI

logo_path = os.path.join(os.path.dirname(__file__), "logo.svg")

# Load SVG
with open(logo_path, "r") as f:
    svg = f.read()

# Convert to base64 (correct way)
svg_base64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")

st.markdown(
    f"""
    <div style="
        background-color: black;
        padding: 20px;
        border-radius: 10px;
        display: flex;
        align-items: center;
    ">
        <img src="data:image/svg+xml;base64,{svg_base64}" width="80" style="margin-right: 20px;" />
        <h1 style="color: white; margin: 0;">
            Rhodes Homebuilder Sales Dashboard
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)



# Connect to Snowflake using Streamlit secrets
conn = snowflake.connector.connect(
    user=st.secrets["SNOWFLAKE_USER"],
    password=st.secrets["SNOWFLAKE_PASSWORD"],
    account=st.secrets["SNOWFLAKE_ACCOUNT"],
    warehouse=st.secrets["SNOWFLAKE_WAREHOUSE"],
    database=st.secrets["SNOWFLAKE_DATABASE"],
    schema=st.secrets["SNOWFLAKE_SCHEMA"],
    role=st.secrets["SNOWFLAKE_ROLE"]
)

query = """
SELECT *
FROM RHODES_DWH.ANALYTICS.FCT_HOMEBUILDER_SALES
"""

df = pd.read_sql(query, conn)

# Sidebar filter
names = ["Region","Community","City","Plan Name","Loan Type","Sales Consultant","Regional Manager","Buyer Source","Status"]

columns = ["REGION","COMMUNITY","CITY","PLAN_NAME","LOAN_TYPE","SALES_CONSULTANT","REGIONAL_MANAGER","BUYER_SOURCE","STATUS"]

perspectives = pd.DataFrame({
    'name': names,
    'column': columns
})

perspective = st.sidebar.selectbox(
    "Select Perspective",
    perspectives["name"].tolist()
)

selected_column = perspectives.loc[
    perspectives["name"] == perspective,
    "column"
].values[0]


def multiselect_filter(dataframe, column, label):
    options = sorted(dataframe[column].dropna().unique().tolist())

    selected = st.sidebar.multiselect(
        label,
        options=["All"] + options,
        default=["All"]
    )

    if "All" in selected or len(selected) == 0:
        return dataframe

    return dataframe[dataframe[column].isin(selected)]


df = multiselect_filter(df, "REGION", "Select Region")
df = multiselect_filter(df, "COMMUNITY", "Select Community")
df = multiselect_filter(df, "CITY", "Select City")
df = multiselect_filter(df, "PLAN_NAME", "Select Plan Name")
df = multiselect_filter(df, "LOAN_TYPE", "Select Loan Type")
df = multiselect_filter(df, "SALES_CONSULTANT", "Select Sales Consultant")
df = multiselect_filter(df, "REGIONAL_MANAGER", "Select Regional Manager")
df = multiselect_filter(df, "BUYER_SOURCE", "Select Buyer Source")
df = multiselect_filter(df, "STATUS", "Select Status")

def range_slider_filter(dataframe, column, label, step, number_format, value_type="int", keep_nulls=False ):
    slider_df = dataframe[dataframe[column].notna()].copy()

    if slider_df.empty:
        st.sidebar.caption(f"{label} not available for current filters")
        return dataframe

    if value_type == "float":
        min_value = float(slider_df[column].min())
        max_value = float(slider_df[column].max())
    else:
        min_value = int(slider_df[column].min())
        max_value = int(slider_df[column].max())

    if min_value == max_value:
        st.sidebar.caption(f"{label}: {min_value}")
        return dataframe

    selected_range = st.sidebar.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=(min_value, max_value),
        step=step,
        format=number_format
    )

    if keep_nulls:
        return dataframe[
            dataframe[column].isna() |
            (
                (dataframe[column] >= selected_range[0]) &
                (dataframe[column] <= selected_range[1])
            )
        ]

    return dataframe[
        (dataframe[column] >= selected_range[0]) &
        (dataframe[column] <= selected_range[1])
    ]


df = range_slider_filter(df, column="CONTRACT_PRICE", label="Contract Price Range", step=1000, number_format="$%d")
df = range_slider_filter(df, column="BASE_PRICE", label="Base Price Range", step=1000, number_format="$%d")
df = range_slider_filter(df, column="UPGRADE_AMOUNT", label="Upgrade Amount Range", step=500, number_format="$%d")
df = range_slider_filter(df, column="INCENTIVE_AMOUNT", label="Incentive Amount Range", step=500, number_format="$%d")
df = range_slider_filter(df, column="PRICE_PER_SQUARE_FOOT", label="Price Per Square Ft Range", step=5, number_format="$%d")
df = range_slider_filter(df, column="AGENT_COMMISSION", label="Agent Commission Range", step=100, number_format="$%d", keep_nulls=True)
df = range_slider_filter(df, column="DAYS_TO_CLOSE", label="Days to Close Range", step=30, number_format="%d", keep_nulls=True)
df = range_slider_filter(df, column="SQFT", label="SQFT Range", step=50, number_format="%d")
df = range_slider_filter(df, column="BEDROOMS", label="Bedrooms Range", step=1, number_format="%d")
df = range_slider_filter(df, column="BATHROOMS", label="Bathrooms Range", step=0.5, number_format="%.1f", value_type="float")

st.sidebar.markdown("**Contract Date Range**")
st.sidebar.caption(
    f"{date_range[0].strftime('%m/%d/%Y')} – {date_range[1].strftime('%m/%d/%Y')}"
)



# Metrics
st.subheader("Sales Overview")

col1, col2, col3 = st.columns(3)

total_sold = df["SOLD_FLAG"].sum()
total_records = len(df)
total_sales = df["CONTRACT_PRICE"].sum()
total_base = df["BASE_PRICE"].sum()
upgrade_amount = df["UPGRADE_AMOUNT"].sum()
incentive_amount = df["INCENTIVE_AMOUNT"].sum()


col1.metric(
    "Total Sales",
    f"${total_sales:,.0f}"
)

col1.markdown(
    f"""
    <div style="font-size:12px; color:gray;">
        <span style="color:#008000;"> ${total_base:,.0f}</span> &nbsp;+&nbsp;
        <span style="color:#020079;">${upgrade_amount:,.0f}</span>&nbsp;&nbsp;
        <span style="color:#FF00FF;">-${incentive_amount:,.0f}</span>
    </div>
    """,
    unsafe_allow_html=True
)

col2.metric(
    "Total Sold",
    total_sold,
    f"{(total_sold / total_records):.1%} of total"
)


col3.metric("Total Under Contract", df["UNDER_CONTRACT_FLAG"].sum())



col4, col5, col6 = st.columns(3)

contract_price = df['CONTRACT_PRICE'].mean()
days_to_close = df['DAYS_TO_CLOSE'].mean()


col4.metric("Avg Contract", f"${contract_price:,.0f}")
col5.metric("Avg Days to Close", f"{days_to_close:,.0f}")

df_dates = df[df["CONTRACT_DATE"].notna()].copy()

if not df_dates.empty:
    min_date = df_dates["CONTRACT_DATE"].min()
    max_date = df_dates["CONTRACT_DATE"].max()

    days = (max_date - min_date).days

    total_sales = df_dates["CONTRACT_PRICE"].sum()

    daily_sales = total_sales / days if days > 0 else 0
    thirty_day_sales = daily_sales * 30
else:
    thirty_day_sales = 0

col6.metric(
    "30-Day Avg Sales",
    f"${thirty_day_sales:,.0f}"
)


category_values = sorted(df[selected_column].dropna().unique().tolist())

palette = px.colors.qualitative.Set2

color_map = {
    value: palette[i % len(palette)]
    for i, value in enumerate(category_values)
}




# Chart 1

sales = df.groupby(selected_column)["CONTRACT_PRICE"].sum().reset_index()
sales = sales.sort_values(by="CONTRACT_PRICE", ascending=False)

fig1 = px.bar(
    sales,
    x=selected_column,
    y="CONTRACT_PRICE",
    color=selected_column, 
    color_discrete_map=color_map,
    title=f"Contracts by {perspective}",
    labels={
        selected_column: perspective,       
        "CONTRACT_PRICE": "Total Sales of Contracts"
    }
)


st.plotly_chart(fig1)

# Chart 2

counts = df.groupby(selected_column)["CONTRACT_ID"].count().reset_index()
counts = counts.sort_values(by="CONTRACT_ID", ascending=False)

fig2 = px.bar(
    counts,
    x=selected_column,
    y="CONTRACT_ID",
    color=selected_column, 
    color_discrete_map=color_map,
    title=f"Count of Contracts by {perspective}",
    labels={
        selected_column: perspective,       
        "CONTRACT_ID": "Count of Contracts"
    }
)


st.plotly_chart(fig2)



# Chart 3

cancellation_rate = df.groupby(selected_column)["CANCELLATION_FLAG"].mean().reset_index()
cancellation_rate = cancellation_rate.sort_values(by="CANCELLATION_FLAG", ascending=False)

fig3 = px.bar(
    cancellation_rate,
    x=selected_column,
    y="CANCELLATION_FLAG",
    color=selected_column, 
    color_discrete_map=color_map,
    title="Cancellation Rate",
    labels={
        selected_column: perspective,       
        "CANCELLATION_FLAG": "Rate Canceled"
    }
)

fig3.update_layout(
    yaxis_tickformat=".2%"  
)

st.plotly_chart(fig3)


df["CONTRACT_DATE"] = pd.to_datetime(df["CONTRACT_DATE"], errors="coerce")
df["MONTH"] = df["CONTRACT_DATE"].dt.to_period("M").dt.to_timestamp()

monthly_sales = (
    df.groupby(["MONTH", selected_column])["CONTRACT_PRICE"]
    .sum()
    .reset_index()
)

fig4 = px.line(
    monthly_sales,
    x="MONTH",
    y="CONTRACT_PRICE",
    color=selected_column,
    color_discrete_map=color_map,
    title=f"Monthly Sales Trend by {perspective}",
    labels={
        "MONTH": "Month",
        "CONTRACT_PRICE": "Total Sales",
        selected_column: perspective
    }
)

fig4.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=",",
    xaxis_title="Month",
    yaxis_title="Total Sales"
)

fig4.update_traces(
    hovertemplate=f"{perspective}: %{{legendgroup}}<br>Month: %{{x|%b %Y}}<br>Sales: $%{{y:,.0f}}<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)


st.subheader("Snowflake Cortex AI Summary")

st.caption(
    "Uses Snowflake Cortex COMPLETE to generate business-friendly insights from the current dashboard perspective and filters."
)

if df.empty:
    st.warning("No data available for the current filters.")
else:
    perspective_summary = (
        df.groupby(selected_column, dropna=False)
        .agg(
            total_sales=("CONTRACT_PRICE", "sum"),
            avg_contract=("CONTRACT_PRICE", "mean"),
            total_base_price=("BASE_PRICE", "sum"),
            avg_base_price=("BASE_PRICE", "mean"),
            cancellation_rate=("CANCELLATION_FLAG", "mean"),
            avg_days_to_close=("DAYS_TO_CLOSE", "mean"),
            sold_units=("SOLD_FLAG", "sum"),
            total_records=("CONTRACT_ID", "count")
        )
        .reset_index()
        .sort_values(by="total_sales", ascending=False)
        .head(10)
    )

    perspective_summary = perspective_summary.round({
        "total_sales": 0,
        "avg_contract": 0,
        "total_base_price": 0,
        "avg_base_price": 0,
        "cancellation_rate": 4,
        "avg_days_to_close": 1,
        "sold_units": 0,
        "total_records": 0
    })

    perspective_text = perspective_summary.to_string(index=False)

    user_question = st.text_input(
        "Ask a question about the current dashboard data",
        placeholder=f"Example: Which {perspective.lower()} should leadership focus on?"
    )

    if st.button("Generate Cortex Insight"):
        prompt = f"""
You are a sales analytics assistant for a homebuilder leadership team.

Use the {perspective} performance summary below to answer in business terms.

{perspective} performance data:
{perspective_text}

Current selected dashboard perspective: {perspective}

User question:
{user_question if user_question.strip() else "Provide an executive summary of performance."}

Provide:
1. Key performance insight
2. Risk or concern
3. Recommendation for leadership

Keep the response concise, business-friendly, and grounded only in the provided data.
"""

        safe_prompt = prompt.replace("'", "''")

        cortex_query = f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-large',
            '{safe_prompt}'
        ) AS AI_SUMMARY
        """

        with st.spinner("Generating Snowflake Cortex insight..."):
            ai_df = pd.read_sql(cortex_query, conn)

        st.markdown("### AI Response")
        st.write(ai_df["AI_SUMMARY"].iloc[0])



client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

with st.expander("💬 Ask the Data", expanded=False):
    st.caption(
        "Ask plain-English questions about the currently filtered dashboard data. "
        "The assistant is grounded in the filtered mart data and column definitions."
    )

    # Column context / data dictionary
    column_context = """
Column definitions:
- CONTRACT_ID: Unique sales contract identifier.
- COMMUNITY: Community or subdivision where the home was sold.
- CITY: City where the community is located.
- REGION: Sales region.
- PLAN_NAME: Home floor plan name.
- SQFT: Home square footage.
- BEDROOMS: Number of bedrooms.
- BATHROOMS: Number of bathrooms.
- BASE_PRICE: Starting/base home price before upgrades and incentives.
- UPGRADE_AMOUNT: Dollar amount of upgrades added to the home.
- INCENTIVE_AMOUNT: Dollar amount of buyer incentives or discounts.
- CONTRACT_PRICE: Final contract sales price.
- CONTRACT_DATE: Date the buyer entered contract.
- CLOSE_DATE: Date the home closed, if closed.
- DAYS_TO_CLOSE: Days between contract date and close date.
- DAYS_TO_CLOSE_CAL: Calculated days to close from dbt logic.
- PRICE_PER_SQUARE_FOOT: Contract price divided by square footage.
- CANCELLATION_FLAG: 1 if canceled, 0 otherwise.
- SOLD_FLAG: 1 if sold/closed, 0 otherwise.
- UNDER_CONTRACT_FLAG: 1 if currently under contract, 0 otherwise.
- STATUS: Current transaction status.
- BUYER_SOURCE: Source/channel that brought the buyer.
- AGENT_COMMISSION: Commission amount.
- LOAN_TYPE: Buyer financing type.
- SALES_CONSULTANT: Sales consultant assigned to the transaction.
- REGIONAL_MANAGER: Regional manager tied to the region.
- SALES_TARGET_UNITS: Regional sales unit target.
- MARGIN_TARGET_PCT: Regional margin target percentage.
"""

    # High-level filtered data context
    filtered_summary = f"""
Current filtered dataset summary:
- Rows: {len(df)}
- Total contract sales: ${df["CONTRACT_PRICE"].sum():,.0f}
- Average contract price: ${df["CONTRACT_PRICE"].mean():,.0f}
- Average base price: ${df["BASE_PRICE"].mean():,.0f}
- Total upgrades: ${df["UPGRADE_AMOUNT"].sum():,.0f}
- Total incentives: ${df["INCENTIVE_AMOUNT"].sum():,.0f}
- Average price per square foot: ${df["PRICE_PER_SQUARE_FOOT"].mean():,.2f}
- Total sold units: {df["SOLD_FLAG"].sum():,.0f}
- Total under contract: {df["UNDER_CONTRACT_FLAG"].sum():,.0f}
- Cancellation rate: {df["CANCELLATION_FLAG"].mean():.2%}
- Average days to close: {df["DAYS_TO_CLOSE"].mean():.1f}
- Current perspective selected: {perspective}
"""

    # Perspective-level summary
    perspective_summary = (
        df.groupby(selected_column, dropna=False)
        .agg(
            total_records=("CONTRACT_ID", "count"),
            total_sales=("CONTRACT_PRICE", "sum"),
            avg_contract_price=("CONTRACT_PRICE", "mean"),
            avg_price_per_sqft=("PRICE_PER_SQUARE_FOOT", "mean"),
            cancellation_rate=("CANCELLATION_FLAG", "mean"),
            sold_units=("SOLD_FLAG", "sum"),
            under_contract_units=("UNDER_CONTRACT_FLAG", "sum"),
            avg_days_to_close=("DAYS_TO_CLOSE", "mean"),
        )
        .reset_index()
        .sort_values("total_sales", ascending=False)
        .head(15)
        .round(2)
    )

    perspective_context = f"""
Performance by selected perspective: {perspective}
{perspective_summary.to_string(index=False)}
"""

    # Small sample of row-level data
    sample_columns = [
        "CONTRACT_ID",
        "COMMUNITY",
        "CITY",
        "REGION",
        "PLAN_NAME",
        "SQFT",
        "BEDROOMS",
        "BATHROOMS",
        "BASE_PRICE",
        "UPGRADE_AMOUNT",
        "INCENTIVE_AMOUNT",
        "CONTRACT_PRICE",
        "CONTRACT_DATE",
        "CLOSE_DATE",
        "DAYS_TO_CLOSE",
        "DAYS_TO_CLOSE_CAL",
        "PRICE_PER_SQUARE_FOOT",
        "CANCELLATION_FLAG",
        "SOLD_FLAG",
        "UNDER_CONTRACT_FLAG",
        "STATUS",
        "BUYER_SOURCE",
        "AGENT_COMMISSION",
        "LOAN_TYPE",
        "SALES_CONSULTANT",
        "REGIONAL_MANAGER",
        "SALES_TARGET_UNITS",
        "MARGIN_TARGET_PCT",
    ]

    available_sample_columns = [c for c in sample_columns if c in df.columns]

    sample_data = (
        df[available_sample_columns]
        .head(25)
        .to_string(index=False)
    )

    user_question = st.text_input(
        "Ask a question",
        placeholder="Example: Which sales consultant should leadership focus on?"
    )

    if st.button("Ask ChatGPT"):
        if df.empty:
            st.warning("No data is available for the current filters.")
        elif not user_question.strip():
            st.warning("Please enter a question.")
        else:
            prompt = f"""
You are a business analytics assistant for a homebuilder sales dashboard.

Answer the user's question using only the provided data context.
Do not invent facts. If the provided data is not enough, say what is missing.
Keep the answer concise, business-friendly, and actionable.

{column_context}

{filtered_summary}

{perspective_context}

Sample row-level data from the current filters:
{sample_data}

User question:
{user_question}
"""

            with st.spinner("Generating answer..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt
                )

            st.markdown("### Answer")
            st.write(response.output_text)