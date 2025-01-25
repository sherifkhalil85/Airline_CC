
# import libraries 
import pandas as pd
import streamlit as st
import plotly_express as px

# Configure page
st.set_page_config(
    layout='wide', page_title='CC Operations', page_icon=':airplane_departure:'
)
############################
# Load data
df = pd.read_csv('data/aggregated2.csv')


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
#############################################################
# Daily operation trend dataframe
dfo= df.groupby(['transaction_date', 'weekDay', 'is_weekend']).agg({
    'call_id': 'count',
    'talkTime': 'mean',
    'waitingTime': 'mean',
    'average_sentiment':'mean'
}).reset_index()

# View selection 
Demo_selection = st.radio('Choose a category:', ['Charts', 'Statistics'])
if Demo_selection == 'Charts':
    with st.container():
        Operation_View = st.selectbox("Please choose the view you want:", ['all', 'highlights', 'WD only', 'weekend Only'])

        if Operation_View == 'all':
            dfo_filtered = dfo
            df_filtered = df
            color1 = None
        elif Operation_View == 'highlights':
            dfo_filtered = dfo
            df_filtered = df
            color1 = 'is_weekend'
        elif Operation_View == 'WD only':
            dfo_filtered = dfo[dfo['is_weekend'] == False]
            df_filtered = df[df['is_weekend'] == False]
            color1 = None
        elif Operation_View == 'weekend Only':
            dfo_filtered = dfo[dfo['is_weekend'] == True]
            df_filtered = df[df['is_weekend'] == True]
            color1 = None

        # Daily trend for calls
        fig = px.bar(dfo_filtered, y='call_id', x='transaction_date', color=color1, template='presentation', title='Daily calls distribution with weekends highlighted', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        col1, col2, col3 = st.columns([15, 0.5, 15])

        with col1:  # Talk time
            fig = px.histogram(df_filtered, x='talkTime', marginal='box', nbins=31, template='presentation', title='TalkTime distribution', color=color1)
            fig.update_traces(marker=dict(line=dict(color='black', width=1.5)))

            st.plotly_chart(fig, use_container_width=True)

        with col3:  # Waiting time
            fig = px.histogram(df_filtered, x='waitingTime', marginal='box', template='presentation', title='Waiting time distribution', color=color1)
            fig.update_traces(marker=dict(line=dict(color='black', width=1.5)))

            st.plotly_chart(fig, use_container_width=True)

    ###########################################################################
    # sentiment vs TT and Waiting time 
        with st.expander('check the Sentiment relationship with TalkTime and Waiting time'):

            TargetV=  st.radio('Choose a scope :', ['talkTime', 'waitingTime'])

            dataSelection = st.radio('Choose a category:', ['Overall', 'daily'])


            if dataSelection =='Overall':
                dfoSource = df
                sizeS= None
                
            elif dataSelection =='daily':
                dfoSource = dfo
                sizeS = 'call_id'

            #measure Corrleation R
            correlation_matrix = dfoSource[[TargetV, 'average_sentiment']].corr()
            correlation_value = correlation_matrix.loc[TargetV,'average_sentiment']
            Determination = correlation_value**2

            # Metrics
            col1,col2 = st.columns(2)

            with col1:
                st.metric(label=f"Correlation between {TargetV} and Sentiment" , value=f"{correlation_value:.3f}")
            with col2:
                st.metric(label=f" Coefficient of Determination for {TargetV} and Average Sentiment", value= f"{Determination:.3f}")

            fig=px.scatter(dfoSource,
             x='average_sentiment'
            , y=TargetV,
            color = 'is_weekend', template='presentation',size=sizeS,
            title=f'{dataSelection} Correlation between {TargetV} and Average Sentiment')
            st.plotly_chart(fig, use_container_width=True)

            


##########################################################
elif Demo_selection == 'Statistics': # showing descriptive statiscs for talk time and waiting time

#  create dataframes  
    tt_stat = df['talkTime'].describe()
    tt_daily = dfo['talkTime'].describe()
    tt_dailyNotWE = df[df['is_weekend'] == False]['talkTime'].describe()
    tt_dailyWE = df[df['is_weekend'] == True]['talkTime'].describe()
    tt = pd.DataFrame([tt_stat, tt_daily, tt_dailyNotWE, tt_dailyWE]).T
    tt.columns = ['Overall Talk Time', 'Daily Talk Time', 'Talk Time in Week Day', 'Talk Time in Weekend']
    tt = tt.applymap(lambda x: f"{x:.2f}" if isinstance(x, float) else x)

    wt_stat = df['waitingTime'].describe()
    wt_daily = dfo['waitingTime'].describe()
    wt_dailyNotWE = df[df['is_weekend'] == False]['waitingTime'].describe()
    wt_dailyWE = df[df['is_weekend'] == True]['waitingTime'].describe()
    wt = pd.DataFrame([wt_stat, wt_daily, wt_dailyNotWE, wt_dailyWE]).T
    wt.columns = ['Overall Waiting Time', 'Daily Waiting Time', 'Waiting Time in Week Day', 'Waiting Time in Weekend']
    wt = wt.applymap(lambda x: f"{x:.2f}" if isinstance(x, float) else x)

   
    col1, col2 =st.columns(2)
    # Talk Time Statistics
    with col1:
        st.write("""
            <style>
            div.border {
                border: 2px solid black;
                padding: 10px;
                background-color: #f0f0f0;
                text-align: waiting time whiskercenter;
                border-radius: 10px;
                margin: 10px 0;
            }
            h2 {
                margin-top: 0;
            }
            </style>
            <div class='border'>
                <h2>Talk Time Statistics</h2>
                <div style='display: flex; align-items: center; justify-content: center;'>
                    <!-- Placeholder for DataFrame -->
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(tt)

        #Talk time whisker
        with st.expander('check daily talk time whisker'):
            fig = px.box(df,  y='talkTime',x= 'transaction_date',color = 'is_weekend', template='presentation', title = ' Talk Time')
            st.plotly_chart(fig, use_container_width=True)


    # Waiting Time Statistics
    with col2:
        st.write("""
            <style>
            div.border {
                border: 2px solid black;
                padding: 10px;
                background-color: #f0f0f0;
                text-align: center;
                border-radius: 10px;
                margin: 10px 0;
            }
            h2 {
                margin-top: 0;
            }
            </style>
            <div class='border'>
                <h2>Waiting Time Statistics</h2>
                <div style='display: flex; align-items: center; justify-content: center;'>
                    <!-- Placeholder for DataFrame -->
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(wt)
        #waiting time  whisker
        with st.expander('check daily waiting time whisker'):
            fig = px.box(df,  y='waitingTime',x= 'transaction_date',color = 'is_weekend', template='presentation', title = ' Talk Time')
            st.plotly_chart(fig, use_container_width=True)
       



