
########## 
# import libraries 
import pandas as pd
import streamlit as st
import plotly.express as px

# Configure page
st.set_page_config(
    layout='wide', page_title='Air Line ', page_icon=':airplane_departure:'
)
##########################################
#configure side page

# Custom CSS for the sidebar
sidebar_style = """
    <style>
    /* Style for the entire sidebar */
    [data-testid="stSidebar"] {
        background-color: #f5f5f5;  /* Light gray background */
        padding: 20px;
        border-right: 2px solid #ddd;  /* Border to separate sidebar */
    }

    /* Style for text elements in the sidebar */
    [data-testid="stSidebar"] div {
        font-size: 18px;
        color: #007BFF;  /* Blue text color */
        margin-bottom: 10px;
        font-weight: bold;
    }

    /* Style for selected items */
    .selected-item {
        background-color: #0056b3;  /* Dark blue background */
        color: white;  /* White font */
        padding: 10px;
        font-size: 18px;
        font-weight: bold;
    }

    /* Hover effect for items */
    [data-testid="stSidebar"] div:hover {
        color: #0056b3;  /* Darker blue when hovering */
        cursor: pointer;
    }
    </style>
"""

# Inject the CSS into the Streamlit app
st.markdown(sidebar_style, unsafe_allow_html=True)

# Sidebar content
st.sidebar.title("Navigation")
st.sidebar.write("Select pages above or any options below from the list:")

# Add hyperlinks to the sidebar
st.sidebar.markdown("[Data Source](https://www.kaggle.com/datasets/origamik/united-airlines-call-center-sentiment-dataset)")
st.sidebar.markdown("[GitHub Repo](https://github.com/sherifkhalil85/Airline_CC/tree/main)")
st.sidebar.markdown("[Contact Me](https://www.linkedin.com/in/sherif-khalil-62b44823)")



####################################
# Load data
df = pd.read_csv('data/aggregated2.csv')


# Initial calculations to create the summary and Metrics
Talktime = df['talkTime'].mean()
DailyDF = df.groupby('transaction_date').agg({'talkTime': 'mean', 'waitingTime': 'mean'}).reset_index()
dailyTT = DailyDF['talkTime'].mean()
WT = df['waitingTime'].mean()
Daily_wt = DailyDF['waitingTime'].mean()
countDays = DailyDF['transaction_date'].shape[0]
df['transaction_date'] = pd.to_datetime(df['transaction_date'])
minDate = df['transaction_date'].min()
maxDate = df['transaction_date'].max()


Calls_count = df['call_id'].count()
Customers_count = df['customer_id'].count()
Customers_distinct = df['customer_id'].nunique()
FCR = 1 - ((Calls_count - Customers_distinct) / Calls_count)

senti = df['average_sentiment'].mean()
Med_sen =df['average_sentiment'].median()
WD = df.groupby('weekDay')['call_id'].count().sort_values(ascending=False).reset_index()
callreason = df.groupby('primary_call_reason')['call_id'].count().sort_values(ascending=False).reset_index()


# Custom CSS for enhancements
st.markdown("""
    <style>
        body {
            background-color: #f6f6f6 !important;
        }
        .stApp {
            background-color: #f6f6f6 !important;
            padding-top: 10px;
        }
        .title {
            background-color: #ffffff;
            color: #616f89;
            padding: 10px;
            text-align: center;
            font-size: 40px;
            font-weight: bold;
            border: 4px solid #000083;
            border-radius: 10px;
            box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.2);
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin-bottom: 20px;
        }
        .metric {
            background-color: #ffffff;
            border: 2px solid #000083;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 25px;
            transition: transform 0.2s ease-in-out;
        }
        .metric:hover {
            box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.3);
            transform: scale(1.05);
        }
        .metric p {
            color: #000083;
            font-size: 26px;
            font-weight: 600;
            font-style: italic;
            text-shadow: 1px 1px 2px #000083;
        }
        .metric h3 {
            margin-bottom: 5px;
            font-size: 20px;
            font-weight: 500;
            color: #999999;
        }
        @media (max-width: 768px) {
            .metric {
                padding: 10px;
            }
            .title {
                font-size: 30px;
            }
            .metric p {
                font-size: 20px;
            }
            .metric h3 {
                font-size: 16px;
            }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">CC Airline Analysis Overview</div>', unsafe_allow_html=True)

with st.expander('View Summary'):

    # Custom CSS for hover and shadow effects
    st.markdown("""
        <style>
        .paper-style {
            background-color: #ffffff;
            border: 2px solid #003366; /* Dark Blue Border */
            padding: 20px;
            font-family: 'Arial', sans-serif;
            font-size: 16px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Subtle shadow */
            margin-bottom: 30px;
            transition: transform 0.2s ease, box-shadow 0.2s ease; /* Smooth transitions */
            max-width: 100%; /* Ensures it doesn't overflow the screen */
            width: auto; /* Adjusts to content dynamically */
        }
        .paper-style:hover {
            transform: scale(1.02); /* Slightly enlarge on hover */
            box-shadow: 0px 8px 12px rgba(0, 0, 0, 0.2); /* Enhanced shadow on hover */
        }
        .header-text {
            font-size: 20px;
            font-weight: bold;
            color: #003366; /* Dark Blue Header */
            margin-bottom: 10px;
        }
        .body-text {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)

    # The summary content formatted into the paper to show summary 
    summary_content = f"""
    <div class="paper-style">
        <div class="header-text">Executive Summary</div>
        <div class="body-text">The exercise contains <strong>{len(df)}</strong> logs.</div>
        <div class="body-text">Total calls = <strong>{Calls_count}</strong> and the contacted customers = <strong>{Customers_count}</strong> with FCR% = <strong>{FCR:.2%}</strong>.</div>
        <div class="body-text">Average Talktime = <strong>{Talktime:.2f}</strong> but daily Talktime = <strong>{dailyTT:.2f}</strong>.</div>
        <div class="body-text">Average sentiment = <strong>{senti:.3f}</strong> and Median = <strong>{Med_sen:.3f}</strong>.</div>
        <div class="body-text">The call reasons include diversity and contain <strong>{callreason.shape[0]}</strong> call reasons.</div>
        <div class="body-text">We will explore the results together to find the main drivers that may enhance sentiment directly, which will improve overall customer experience indirectly.</div>
    </div>
    """

    # Display the formatted summary
    st.markdown(summary_content, unsafe_allow_html=True)



with st.expander('view metrics'): # Metrics

    # Columns for layout
    col1, col2, col3 = st.columns(3)

    # Column 1 metrics
    with col1:
        st.markdown(f'''
            <div class="metric">
                <h3>📞 Total Calls</h3>
                <p>{Calls_count}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>👥 Contacted Customers</h3>
                <p>{Customers_count}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>📊 FCR%</h3>
                <p>{FCR:.2%}</p>
            </div>
        ''', unsafe_allow_html=True)

    # Column 2 metrics
    with col2:
        st.markdown(f'''
            <div class="metric">
                <h3>🗣️ Average Talk Time</h3>
                <p>{Talktime:.2f}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>🔃 Average Daily Talk Time</h3>
                <p>{dailyTT:.2f}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>⏳ Average Daily Waiting Time</h3>
                <p>{Daily_wt:.2f}</p>
            </div>
        ''', unsafe_allow_html=True)

    # Column 3 metrics
    with col3:
        st.markdown(f'''
            <div class="metric">
                <h3>🗓️ Rush Day</h3>
                <p>{WD['weekDay'][0]}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>📊 Average Sentiment</h3>
                <p>{senti:.2f}</p>
            </div>
        ''', unsafe_allow_html=True)
        st.markdown(f'''
            <div class="metric">
                <h3>🎯 Top Call Reason</h3>
                <p>{callreason['primary_call_reason'][0]}</p>
            </div>
        ''', unsafe_allow_html=True)
#########################################

# show images 

image1= 'https://www.vonage.com/cdn-cgi/image/fit=contain,width=620,onerror=redirect/content/dam/vonage/us-en/resources/imagery/article-imagery/SEO-Call-Center-Managment-Blog.jpg'
image2='https://www.oag.com/hubfs/Untitled%20design%20%281%29-2.jpg'
image3='https://www.aviationtoday.com/wp-content/uploads/2015/03/SITA.jpg'
col3 = st.columns([10,1,10])
col1, col2, col3 = st.columns([10, 1, 10])

# Display images in the appropriate columns
with col1:
    st.image(image1, use_container_width =True)

with col3:
    st.image(image2, use_container_width =True)
    st.image(image3, use_container_width =True)
   
