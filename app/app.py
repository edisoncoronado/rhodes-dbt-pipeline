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

# Chart 1
# st.subheader("Sales by Region")
# st.bar_chart(df.groupby("REGION")["CONTRACT_ID"].count())

region_sales = df.groupby("REGION")["CONTRACT_ID"].count().reset_index()
region_sales = region_sales.sort_values(by="CONTRACT_ID", ascending=False)

fig = px.bar(
    region_sales,
    x="REGION",
    y="CONTRACT_ID",
    color="REGION", 
    title="Sales by Region",
    labels={"CONTRACT_ID": "Total Sales"},
    color_discrete_sequence=px.colors.qualitative.Pastel
)


st.plotly_chart(fig)

# Chart 2
st.subheader("Cancellation Rate")
st.bar_chart(df.groupby("REGION")["CANCELLATION_FLAG"].mean())

# Chart 3
st.subheader("Avg Price per Sqft")
st.bar_chart(df.groupby("REGION")["PRICE_PER_SQUARE_FOOT"].mean())