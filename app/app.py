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


 
region = st.sidebar.selectbox("Filter Region", ["All"] + sorted(df["REGION"].dropna().unique().tolist()))
if region != "All":
    df = df[df["REGION"] == region]

community = st.sidebar.selectbox("Filter Community", ["All"] + sorted(df["COMMUNITY"].dropna().unique().tolist()))
if community != "All":
    df = df[df["COMMUNITY"] == community]

city = st.sidebar.selectbox("Filter City", ["All"] + sorted(df["CITY"].dropna().unique().tolist()))
if city != "All":
    df = df[df["CITY"] == city]

plan_name = st.sidebar.selectbox("Filter Plan Name", ["All"] + sorted(df["PLAN_NAME"].dropna().unique().tolist()))
if plan_name != "All":
    df = df[df["PLAN_NAME"] == plan_name]

loan_type = st.sidebar.selectbox("Filter Loan Type", ["All"] + sorted(df["LOAN_TYPE"].dropna().unique().tolist()))
if loan_type != "All":
    df = df[df["LOAN_TYPE"] == loan_type]

sales_consultant = st.sidebar.selectbox("Filter Sales Consultant", ["All"] + sorted(df["SALES_CONSULTANT"].dropna().unique().tolist()))
if sales_consultant != "All":
    df = df[df["SALES_CONSULTANT"] == sales_consultant]

regional_manager = st.sidebar.selectbox("Filter Regional Manager", ["All"] + sorted(df["REGIONAL_MANAGER"].dropna().unique().tolist()))
if regional_manager != "All":
    df = df[df["REGIONAL_MANAGER"] == regional_manager]

buyer_source = st.sidebar.selectbox("Filter Buyer Source", ["All"] + sorted(df["BUYER_SOURCE"].dropna().unique().tolist()))
if buyer_source != "All":
    df = df[df["BUYER_SOURCE"] == buyer_source]

status = st.sidebar.selectbox("Filter Status", ["All"] + sorted(df["STATUS"].dropna().unique().tolist()))
if status != "All":
    df = df[df["STATUS"] == status]


min_price = int(df["CONTRACT_PRICE"].min())
max_price = int(df["CONTRACT_PRICE"].max())
price_range = st.sidebar.slider(
    "Contract Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1000,
    format="$%d"
)
df = df[
    (df["CONTRACT_PRICE"] >= price_range[0]) &
    (df["CONTRACT_PRICE"] <= price_range[1])
]

min_base_price = int(df["BASE_PRICE"].min())
max_base_price = int(df["BASE_PRICE"].max())
base_price_range = st.sidebar.slider(
    "Base Price Range",
    min_value=min_base_price,
    max_value=max_base_price,
    value=(min_base_price, max_base_price),
    step=1000,
    format="$%d"
)
df = df[
    (df["BASE_PRICE"] >= base_price_range[0]) &
    (df["BASE_PRICE"] <= base_price_range[1])
]

min_upgrade_amount = int(df["UPGRADE_AMOUNT"].min())
max_upgrade_amount = int(df["UPGRADE_AMOUNT"].max())
upgrade_amount_range = st.sidebar.slider(
    "Upgrade Amount Range",
    min_value=min_upgrade_amount,
    max_value=max_upgrade_amount,
    value=(min_upgrade_amount, max_upgrade_amount),
    step=500,
    format="$%d"
)
df = df[
    (df["UPGRADE_AMOUNT"] >= upgrade_amount_range[0]) &
    (df["UPGRADE_AMOUNT"] <= upgrade_amount_range[1])
]

min_incentive_amount = int(df["INCENTIVE_AMOUNT"].min())
max_incentive_amount = int(df["INCENTIVE_AMOUNT"].max())
incentive_amount_range = st.sidebar.slider(
    "Incentive Amount Range",
    min_value=min_incentive_amount,
    max_value=max_incentive_amount,
    value=(min_incentive_amount, max_incentive_amount),
    step=500,
    format="$%d"
)
df = df[
    (df["INCENTIVE_AMOUNT"] >= incentive_amount_range[0]) &
    (df["INCENTIVE_AMOUNT"] <= incentive_amount_range[1])
]


min_ppsf = int(df["PRICE_PER_SQUARE_FOOT"].min())
max_ppsf = int(df["PRICE_PER_SQUARE_FOOT"].max())
ppsf_range = st.sidebar.slider(
    "Price Per Square Ft Range",
    min_value=min_ppsf,
    max_value=max_ppsf,
    value=(min_ppsf, max_ppsf),
    step=5,
    format="$%d"
)
df = df[
    (df["PRICE_PER_SQUARE_FOOT"] >= ppsf_range[0]) &
    (df["PRICE_PER_SQUARE_FOOT"] <= ppsf_range[1])
]


commission_df = df[df["AGENT_COMMISSION"].notna()]
min_commission = int(commission_df["AGENT_COMMISSION"].min())
max_commission = int(commission_df["AGENT_COMMISSION"].max())
commission_range = st.sidebar.slider(
    "Agent Commission Range",
    min_value=min_commission,
    max_value=max_commission,
    value=(min_commission, max_commission),
    step=100,
    format="$%d"
)
df = df[
    (df["AGENT_COMMISSION"].isna()) |   
    (
        (df["AGENT_COMMISSION"] >= commission_range[0]) &
        (df["AGENT_COMMISSION"] <= commission_range[1])
    )
]


days_closed_df = df[df["DAYS_TO_CLOSE"].notna()].copy()

if not days_closed_df.empty:
    min_days_closed = int(days_closed_df["DAYS_TO_CLOSE"].min())
    max_days_closed = int(days_closed_df["DAYS_TO_CLOSE"].max())

    days_closed_range = st.sidebar.slider(
        "Days to Close Range",
        min_value=min_days_closed,
        max_value=max_days_closed,
        value=(min_days_closed, max_days_closed),
        step=30,
        format="%d"
    )

    df = df[
        (df["DAYS_TO_CLOSE"].isna()) |
        (
            (df["DAYS_TO_CLOSE"] >= days_closed_range[0]) &
            (df["DAYS_TO_CLOSE"] <= days_closed_range[1])
        )
    ]


min_sqft = int(df["SQFT"].min())
max_sqft = int(df["SQFT"].max())
sqft_range = st.sidebar.slider(
    "SQFT Range",
    min_value=min_sqft,
    max_value=max_sqft,
    value=(min_sqft, max_sqft),
    step=50,
    format="%d"
)
df = df[
    (df["SQFT"] >= sqft_range[0]) &
    (df["SQFT"] <= sqft_range[1])
]

min_bedrooms = int(df["BEDROOMS"].min())
max_bedrooms = int(df["BEDROOMS"].max())
bedrooms_range = st.sidebar.slider(
    "Bedrooms Range",
    min_value=min_bedrooms,
    max_value=max_bedrooms,
    value=(min_bedrooms, max_bedrooms),
    step=1,
    format="%d"
)
df = df[
    (df["BEDROOMS"] >= bedrooms_range[0]) &
    (df["BEDROOMS"] <= bedrooms_range[1])
]

min_bathrooms = float(df["BATHROOMS"].min())
max_bathrooms = float(df["BATHROOMS"].max())
bathrooms_range = st.sidebar.slider(
    "Bathrooms Range",
    min_value=min_bathrooms,
    max_value=max_bathrooms,
    value=(min_bathrooms, max_bathrooms),
    step=0.5,
    format="%.1f"
)
df = df[
    (df["BATHROOMS"] >= bathrooms_range[0]) &
    (df["BATHROOMS"] <= bathrooms_range[1])
]



df["CONTRACT_DATE"] = pd.to_datetime(df["CONTRACT_DATE"], errors="coerce")
df = df[df["CONTRACT_DATE"].notna()]

min_date = df["CONTRACT_DATE"].min().date()
max_date = df["CONTRACT_DATE"].max().date()

date_range = st.sidebar.date_input(
    "Contract Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
   label_visibility="collapsed"
)

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