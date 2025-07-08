
import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configuration
st.set_page_config(page_title="Sales & Conversion Dashboard", page_icon=":bar_chart:", layout="wide")

# ---- LOAD DATA ----
@st.cache_data
def get_data():
    # Sales conversion data
    df_conv = pd.read_csv("sales_data.csv", parse_dates=["Date"])
    df_conv["Month"] = df_conv["Date"].dt.to_period('M').astype(str)

    # Retail sales data (sample)
    df_sales = pd.read_excel(
        io="supermarkt_sales.xlsx",
        engine="openpyxl",
        sheet_name="Sales",
        skiprows=3,
        usecols="B:R",
        nrows=1000,
    )
    df_sales["hour"] = pd.to_datetime(df_sales["Time"], format="%H:%M:%S").dt.hour

    return df_conv, df_sales

df_conv, df_sales = get_data()

# ---- SIDEBAR FILTERS ----
st.sidebar.header("🔍 Filter Options")

st.sidebar.subheader("Lead Conversion Filters")
sources = st.sidebar.multiselect("Lead Source:", options=df_conv['Source'].unique(), default=df_conv['Source'].unique())
date_range = st.sidebar.date_input("Date Range:", [df_conv['Date'].min(), df_conv['Date'].max()])

st.sidebar.subheader("Retail Sales Filters")
city = st.sidebar.multiselect("City:", options=df_sales["City"].unique(), default=df_sales["City"].unique())
customer_type = st.sidebar.multiselect("Customer Type:", options=df_sales["Customer_type"].unique(), default=df_sales["Customer_type"].unique())
gender = st.sidebar.multiselect("Gender:", options=df_sales["Gender"].unique(), default=df_sales["Gender"].unique())

# ---- FILTERED DATA ----
conv_mask = (df_conv['Source'].isin(sources)) & (df_conv['Date'] >= pd.to_datetime(date_range[0])) & (df_conv['Date'] <= pd.to_datetime(date_range[1]))
df_conv_filt = df_conv[conv_mask]

sales_mask = (df_sales["City"].isin(city)) & (df_sales["Customer_type"].isin(customer_type)) & (df_sales["Gender"].isin(gender))
df_sales_filt = df_sales[sales_mask]

# ---- METRICS SECTION ----
st.title("📊 Combined Sales & Conversion Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Leads", len(df_conv_filt))
with col2:
    st.metric("Converted Leads", df_conv_filt['Converted'].sum())
with col3:
    st.metric("Conversion Rate (%)", round((df_conv_filt['Converted'].sum() / len(df_conv_filt)) * 100, 2) if len(df_conv_filt) else 0)

col4, col5, col6 = st.columns(3)
total_sales = int(df_sales_filt["Total"].sum())
avg_rating = round(df_sales_filt["Rating"].mean(), 1)
star_rating = ":star:" * int(round(avg_rating, 0))
avg_sales = round(df_sales_filt["Total"].mean(), 2)

with col4:
    st.metric("Total Sales ($)", f"{total_sales:,}")
with col5:
    st.metric("Average Rating", f"{avg_rating} {star_rating}")
with col6:
    st.metric("Avg Sale/Transaction", f"{avg_sales}")

st.markdown("---")

# ---- VISUALS SECTION ----
st.subheader("📈 Monthly Lead Conversions")
monthly_conversion = df_conv_filt[df_conv_filt['Converted'] == 1].groupby("Month").size().reset_index(name='Conversions')
fig_conv = px.line(monthly_conversion, x='Month', y='Conversions', markers=True)
st.plotly_chart(fig_conv, use_container_width=True)

st.subheader("🔄 Sales Funnel View")
funnel = df_conv_filt['Stage'].value_counts().reset_index()
funnel.columns = ['Stage', 'Count']
fig_funnel = px.funnel(funnel, x='Count', y='Stage')
st.plotly_chart(fig_funnel, use_container_width=True)

# ---- RETAIL CHARTS ----
st.subheader("📊 Retail: Sales by Product Line & Hour")
left_col, right_col = st.columns(2)

sales_by_product = df_sales_filt.groupby("Product line")["Total"].sum().sort_values().reset_index()
fig_prod = px.bar(sales_by_product, x='Total', y='Product line', orientation='h', color_discrete_sequence=['#0083B8'], title="Sales by Product Line")
fig_prod.update_layout(template="plotly_white", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))

sales_by_hour = df_sales_filt.groupby("hour")["Total"].sum().reset_index()
fig_hour = px.bar(sales_by_hour, x='hour', y='Total', color_discrete_sequence=['#0083B8'], title="Sales by Hour")
fig_hour.update_layout(template="plotly_white", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=False), xaxis=dict(tickmode="linear"))

left_col.plotly_chart(fig_hour, use_container_width=True)
right_col.plotly_chart(fig_prod, use_container_width=True)

# ---- HIDE DEFAULT STREAMLIT STYLE ----
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.caption("Built by Harsh Saini ✨")
