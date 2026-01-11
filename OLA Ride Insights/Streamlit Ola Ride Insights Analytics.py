import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import mysql.connector

# Change these DB details to match the Connection setup
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "vishal458"
DB_NAME = "ola ride insight analysis"  

TABLE_NAME = "ola_dataset"  

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

#---- We can simply copy an emoji from an external source or use a system keyboard shortcut to paste it directly into our Python string. 
#---- Popular Shortcodes- :bar_chart: for 📊, :star: for ⭐

st.set_page_config(page_title="OLA Ride Insights", layout="wide")
st.title("🚖 OLA Ride Insights")

# Check Error Handeling
try:
    df_sample = run_query(f"SELECT * FROM {TABLE_NAME} LIMIT 10")
    st.success("Connected to MySQL and fetched sample data.")
    st.dataframe(df_sample)
except Exception as e:
    st.error(f"Connection/query failed: {e}")
    st.stop()

# KPIs (From SQL table)
st.subheader("Top Metrics (SQL)")
df_success = run_query(f"SELECT * FROM {TABLE_NAME} WHERE Booking_Status='Success'")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Successful Rides", f"{len(df_success):,}")
col2.metric("Total Rides Booking", run_query(f"SELECT COUNT(*) AS c FROM {TABLE_NAME}")["c"].iloc[0])
col3.metric("Avg. Ride Distance", f"{df_success['Ride_Distance'].mean():.2f}")
col4.metric("Avg. Booking Revenue", f"₹{df_success['Booking_Value'].mean():.2f}")

st.subheader("SQL Questions and Answers")
questions = {
    "Successful bookings": f"SELECT * FROM {TABLE_NAME} WHERE Booking_Status='Success'",
    "Avg distance per vehicle": f"SELECT Vehicle_Type, ROUND(AVG(Ride_Distance),2) AS Avg_Ride_Distance FROM {TABLE_NAME} WHERE Ride_Distance>0 GROUP BY Vehicle_Type ORDER BY Avg_Ride_Distance DESC",
    "Total cancelled by customers": f"SELECT COUNT(*) AS Total_Customer_Cancellations FROM {TABLE_NAME} WHERE Booking_Status='Canceled by Customer'",
    "Top 5 customers by rides": f"SELECT Customer_ID, COUNT(*) AS Total_Rides FROM {TABLE_NAME} GROUP BY Customer_ID ORDER BY Total_Rides DESC LIMIT 5",
    "Driver cancellations breakdown": f"SELECT Incomplete_Rides_Reason, COUNT(*) AS Total FROM {TABLE_NAME} WHERE Booking_Status='Canceled by Driver' GROUP BY Incomplete_Rides_Reason ORDER BY Total DESC",
    "Revenue by payment method": f"SELECT Payment_Method, ROUND(SUM(Booking_Value),2) AS Total_Revenue FROM {TABLE_NAME} WHERE Booking_Status='Success' GROUP BY Payment_Method ORDER BY Total_Revenue DESC",
    "Avg customer rating by vehicle": f"SELECT Vehicle_Type, ROUND(AVG(Customer_Rating),2) AS Avg_Customer_Rating FROM {TABLE_NAME} GROUP BY Vehicle_Type ORDER BY Avg_Customer_Rating DESC",
    "Max & Min driver ratings for Prime Sedan": f"SELECT MAX(Driver_Ratings) AS Max_Rating,MIN(Driver_Ratings) AS Min_Rating FROM {TABLE_NAME} WHERE Vehicle_Type = 'Prime Sedan'",
    "Rides paid via UPI": f"SELECT * FROM {TABLE_NAME} WHERE Payment_Method = 'UPI'",
    "Total booking value of successful rides": f"SELECT SUM(Booking_Value) AS Total_Revenue FROM {TABLE_NAME} WHERE Booking_Status = 'Success'",
    "List all Incomplete rides with reason": f"SELECT Booking_ID, Booking_Status, Incomplete_Rides_Reason FROM {TABLE_NAME} WHERE Booking_Status <> 'Success'",
}

selected = st.selectbox("Choose question", list(questions.keys()))
df_answer = run_query(questions[selected])
st.write(f"### Answer: {selected}")
st.dataframe(df_answer)


st.divider()

# ---------- LOAD CSV DATA ----------
@st.cache_data
def load_csv():
    return pd.read_csv("E:/Analytics PDF/OLA Ride Insight/OLA_DataSet.csv")  # File Location

df = load_csv()

# ---------- ADD NEW COLUMNS ----------
df["Ride_Cancelled_By_Customer"] = df["Booking_Status"].apply(
    lambda x: 1 if x == "Canceled by Customer" else 0
)

df["Ride_Cancelled_By_Driver"] = df["Booking_Status"].apply(
    lambda x: 1 if x == "Canceled by Driver" else 0
)

#st.subheader("Cancellation Flags")
#st.dataframe(df[["Booking_Status", "Ride_Cancelled_By_Customer", "Ride_Cancelled_By_Driver"]].head(20))


# ---------- BASIC CLEANING FOR ERROR ----------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date'])


# ---------- FILTERS ----------
st.sidebar.header("🔍 Filters")

# Date filter
min_date = df['Date'].min()
max_date = df['Date'].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Driver Ratings filter
status_filter = st.sidebar.selectbox(
    "Select Driver Ratings",
    options=["All"] + sorted(df['Driver_Ratings'].dropna().unique()),
    #default=sorted(df['Driver_Ratings'].dropna().unique())
)

# Driver Ratings filter
status_filter = st.sidebar.selectbox(
    "Select Customer Ratings",
    options=["All"] + sorted(df['Customer_Rating'].dropna().unique()),
    #default=sorted(df['Customer_Rating'].dropna().unique())
)


# Vehicle filter
vehicle_filter = st.sidebar.multiselect(
    "Select Vehicle Type",
    options= sorted(df['Vehicle_Type'].dropna().unique()),
    default= sorted(df['Vehicle_Type'].dropna().unique()) 
)

# Booking status filter
status_filter = st.sidebar.multiselect(
    "Select Booking Status",
    options=sorted(df['Booking_Status'].dropna().unique()),
    default=sorted(df['Booking_Status'].dropna().unique())
)

# Payment Method filter
status_filter = st.sidebar.multiselect(
    "Select Payment Method",
    options=sorted(df['Payment_Method'].dropna().unique()),
    default=sorted(df['Payment_Method'].dropna().unique())
)


# Convert tuple to dates
start_date, end_date = date_range

filtered_df = df[
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date)) &
    (df['Vehicle_Type'].isin(vehicle_filter)) &
    (df['Booking_Status'].isin(status_filter))
]

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [ r"$\Large \textsf{📊 Overall}$",
    r"$\Large \textsf{🚗 Vehicle Type}$",
    r"$\Large \textsf{💰 Revenue}$",
    r"$\Large \textsf{❌ Cancellation}$",
    r"$\Large \textsf{⭐ Ratings}$"]
)
#st.latex(r"\Huge \text{Enlarged Word}") to make text big in size

with tab1:
    st.header("📊 Overall Analysis")  #

    col1, col2, col3, col4, col5, col6, col7  = st.columns(7)
    
    # Custom CSS to make all metric values green
    st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        color: green !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1.metric("Total Booking Value", f"₹{df['Booking_Value'].sum()/1e6:.2f}M")
    col2.metric("Total Rides Booking", f"{len(df):,.2f}")
    col3.metric("Avg. Booking Revenue", f"₹{df['Booking_Value'].mean():.2f}")
    col4.metric("Avg Customer Rating", f"{df['Customer_Rating'].median():.2f}")
    col5.metric("Avg Driver Rating", f"{df['Driver_Ratings'].median():.2f}")
    col6.metric("Avg. C_CTAT", f"₹{df['C_TAT'].mean():.2f}")
    col7.metric("Avg. V_TAT", f"₹{df['V_TAT'].mean():.2f}")

    st.write("---")

    # Booking Status Pie
    st.subheader("Booking Status Breakdown")
    status_df = df['Booking_Status'].value_counts().reset_index()
    status_df.columns = ['Status', 'Count']
    st.altair_chart(
        alt.Chart(status_df).mark_arc().encode(
            theta='Count',
            color='Status',
            tooltip=['Status','Count']
        ),
        use_container_width=True
    )

    # Ride Volume Over Time
    st.subheader("Ride Volume Over Time")
    trend = df.groupby('Date')['Booking_ID'].count().reset_index()
    trend.columns = ['Date','Count']
    st.line_chart(trend, x='Date', y='Count')
    
    
with tab3:
    st.header("💰 Revenue Analysis")

    st.subheader("Top 5 Customers by Booking Value")
    cust = df.groupby('Customer_ID')['Booking_Value'].sum().nlargest(5)
    st.bar_chart(cust)

    st.subheader("Revenue by Payment Method")
    pay = df.groupby('Payment_Method')['Booking_Value'].sum()
    st.bar_chart(pay)

    st.subheader("Ride Distance Trend")
    dist = df.groupby('Date')['Ride_Distance'].sum()
    st.line_chart(dist)


with tab4:
    st.header("❌ Cancellation Analysis")

    total_cancel = len(df[df['Booking_Status']!='Success'])
    st.metric("Total Cancelled Rides", f"{total_cancel:,}")

    cust_cancel = len(df[df['Booking_Status']=='Canceled by Customer'])
    st.metric("Cancelled by Customer", f"{cust_cancel:,}")

    driver_cancel = len(df[df['Booking_Status']=='Canceled by Driver'])
    st.metric("Cancelled by Driver", f"{driver_cancel:,}")

    st.subheader("Customer Cancellation Reasons")
    c_reason = df[df['Booking_Status']=='Canceled by Customer']['Incomplete_Rides_Reason'].value_counts()
    st.bar_chart(c_reason)

    st.subheader("Driver Cancellation Reasons")
    d_reason = df[df['Booking_Status']=='Canceled by Driver']['Incomplete_Rides_Reason'].value_counts()
    st.bar_chart(d_reason)


with tab5:
    st.header("⭐ Ratings Analysis")

    col1, col2 = st.columns(2)

    col1.metric("Avg Customer Rating", round(df['Customer_Rating'].mean(),2))
    col2.metric("Avg Driver Rating", round(df['Driver_Ratings'].mean(),2))

    st.subheader("Customer Rating by Vehicle Type")
    cust = df.groupby('Vehicle_Type')['Customer_Rating'].mean()
    st.bar_chart(cust)

    st.subheader("Driver Rating by Vehicle Type")
    drv = df.groupby('Vehicle_Type')['Driver_Ratings'].mean()
    st.bar_chart(drv)
    

with tab2:
    st.header("🚗 Vehicle Type Analysis")

    vt = df.groupby('Vehicle_Type').agg({
        'Booking_Value':'sum',
        'Ride_Distance':'sum'
    }).reset_index()

    vt['Total_Booking_Value'] = vt['Booking_Value']/1e6

    st.subheader("Vehicle Type by Total Distance")
    st.bar_chart(vt, x='Vehicle_Type', y='Ride_Distance')

    st.subheader("Vehicle Type by Revenue (Millions)")
    st.bar_chart(vt, x='Vehicle_Type', y='Total_Booking_Value')
    
    # 1. Load sample data (replace with your actual data source, e.g., a CSV file)
    # This DataFrame simulates raw ride data for different vehicles.
    data = {
        'Vehicle_Type': ['Bike', 'eBike', 'Mini', 'Prime Plus', 'Prime Sedan', 'Prime SUV', 'Auto'],
        'Ride_Distance': [15.53, 15.58, 15.51, 15.45, 15.76, 15.27, 6.24]
    }
    df = pd.DataFrame(data)

    # 2. Calculate the total metrics you want to display
    # Avg. Ride Distance is 14.19
    # We can calculate the total of our sample data:
    avg_distance = df.groupby('Vehicle_Type')['Ride_Distance'].mean().reset_index()

    #Sort the results in descending order of average distance
    sorted_avg_distances = avg_distance.sort_values(by='Ride_Distance', ascending=False)

    #Select the top 5 rows
    top_5_vehicles = sorted_avg_distances.head(5)

    # 5. Display the results in Streamlit
    st.subheader("Top 5 Vehicle Type By Ride Distance")
    st.dataframe(
        top_5_vehicles, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Ride_Distance": st.column_config.NumberColumn(
                "Average Distance (km)",
                    format="%.2f km"
                )
            }
        )


