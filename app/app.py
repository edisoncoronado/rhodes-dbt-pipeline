import streamlit as st
import pandas as pd
import snowflake.connector
import plotly.express as px

st.title("Rhodes Homebuilder Sales Dashboard")

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
region = st.sidebar.selectbox("Select Region", ["All"] + sorted(df["REGION"].dropna().unique().tolist()))

if region != "All":
    df = df[df["REGION"] == region]

# Metrics
st.subheader("Sales Overview")

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", len(df))
col2.metric("Avg Price", f"${df['CONTRACT_PRICE'].mean():,.0f}")
col3.metric("Avg Price per Sqft", f"${df['PRICE_PER_SQUARE_FOOT'].mean():,.2f}")

color_map = {
    "Rio Grande Valley": "#5DA5A4",   # teal
    "South Texas": "#E3C26F",         # gold
    "Coastal Bend": "#E88E64"         # orange
}


# Chart 1
# st.subheader("Sales by Region")
# st.bar_chart(df.groupby("REGION")["CONTRACT_ID"].count())

region_sales = df.groupby("REGION")["CONTRACT_ID"].count().reset_index()
region_sales = region_sales.sort_values(by="CONTRACT_ID", ascending=False)

fig1 = px.bar(
    region_sales,
    x="REGION",
    y="CONTRACT_ID",
    color="REGION", 
    color_discrete_map=color_map,
    title="Sales by Region",
    labels={"CONTRACT_ID": "Total Sales"}
)


st.plotly_chart(fig1)

# Chart 2
# st.subheader("Cancellation Rate")
# st.bar_chart(df.groupby("REGION")["CANCELLATION_FLAG"].mean())

cancellation_rate = df.groupby("REGION")["CANCELLATION_FLAG"].mean().reset_index()
cancellation_rate = cancellation_rate.sort_values(by="CANCELLATION_FLAG", ascending=False)

fig2 = px.bar(
    cancellation_rate,
    x="REGION",
    y="CANCELLATION_FLAG",
    color="REGION", 
    color_discrete_map=color_map,
    title="Cancellation Rate",
    labels={"CANCELLATION_FLAG": "Rate Canceled"}
)

st.plotly_chart(fig2)

# Chart 3
st.subheader("Avg Price per Sqft")
st.bar_chart(df.groupby("REGION")["PRICE_PER_SQUARE_FOOT"].mean())