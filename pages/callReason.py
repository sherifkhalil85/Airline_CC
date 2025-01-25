import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go


# Configure page
st.set_page_config(
    layout='wide', page_title='Air Line - CC Call reasons', page_icon=':airplane_departure:'
)


# Load data
df = pd.read_csv('data/aggregated2.csv')

#############################################################################
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


##############################################
# create data frames to be manipulated and selected based on ST.radio and user selection + t create Pareto

reasons = df.groupby('primary_call_reason')['call_id'].count().reset_index().sort_values(by='call_id',ascending=False)
reasons['cumulative_percentage'] = reasons['call_id'].cumsum() / reasons['call_id'].sum() * 100

R_wdall= df.groupby(['primary_call_reason','is_weekend'])['call_id'].count().reset_index()
R_WD = R_wdall[R_wdall['is_weekend'] == False].sort_values(by='call_id',ascending=False)
R_WD['cumulative_percentage'] = R_WD['call_id'].cumsum() / R_WD['call_id'].sum() * 100

R_WE = R_wdall[R_wdall['is_weekend'] == True].sort_values(by='call_id',ascending=False)
R_WE['cumulative_percentage'] = R_WE['call_id'].cumsum() / R_WE['call_id'].sum() * 100
###################################################

# prepare all slicers and selections with button to download targted data per call reasons
with st.container(): 
    col1,col2,col3 = st.columns(3)
    with col1:

        R_selection = st.radio('Choose a view:', ['Reasons Count', 'Pareto'],horizontal=True)
    with col2:
        WD_selection = st.radio('Choose a scope:', ['All','Weekday', 'Weekend'],horizontal=True)

    source =reasons
    if WD_selection == 'All':
        source = reasons
    elif WD_selection == 'Weekday':
        source = R_WD
    elif WD_selection == 'Weekend':
        source = R_WE

    # Convert the DataFrame to CSV
    csv = source.to_csv(index=False)

    with col3:# Create a download button
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name='source_data.csv',
            mime='text/csv'
        )
##########################################


if R_selection == 'Reasons Count':

    fig= px.bar(source, y='call_id', x='primary_call_reason',template='presentation',text_auto=True, title='Call reasons total'.title())
    st.plotly_chart(fig,use_container_width=True)

if R_selection == 'Pareto':

  
    # Create a Pareto chart
    fig = go.Figure()

    # Add bars for call counts
    fig.add_traces([
        go.Bar(x=source['primary_call_reason'], y=source['call_id'], text=source['call_id'], textposition='auto', name='Call Count'),
        go.Scatter(x=source['primary_call_reason'], y=source['cumulative_percentage'], mode='lines+markers', name='Cumulative Percentage', yaxis='y2')
    ])

    # Find the first datapoint above 60% and 80%
    above_60 = source[source['cumulative_percentage'] > 60].iloc[0]
    above_80 = source[source['cumulative_percentage'] > 80].iloc[0]

    # Add annotations for the datapoints above 60% and 80% with black text color
    fig.add_annotation(
        x=above_60['primary_call_reason'], 
        y=above_60['cumulative_percentage'], 
        text=f"60%: {above_60['primary_call_reason']}", 
        showarrow=True, 
        arrowhead=2, 
        ax=0, 
        ay=-200,
          font=dict(color="black", size=15)
    )

    fig.add_annotation(
        x=above_80['primary_call_reason'], 
        y=above_80['cumulative_percentage'], 
        text=f"80%: {above_80['primary_call_reason']}", 
        showarrow=True, 
        arrowhead=2, 
        ax=0, 
        ay=-220,
          font=dict(color="black", size=15)
    )

    fig.update_layout(
        template='presentation',
        title='Pareto Chart of Call Reasons',
        xaxis_title='Primary Call Reason',
        yaxis=dict(title='Number of Calls'),
        yaxis2=dict(title='Cumulative Percentage', overlaying='y', side='right', showgrid=False),
        legend=dict(x=0.1, y=1.1),
        width=800,
        height=500
    )

    # Display the Pareto chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


#############################
#create pivottable to be used in analyzing talk time per call reasons
reasonsAHT =  df.pivot_table(values=['call_id', 'talkTime'], index='primary_call_reason', aggfunc={'call_id': 'count', 'talkTime': 'mean'} )
reasonsAHT = reasonsAHT.sort_values(by='call_id', ascending=False).reset_index()

# Format talkTime to two decimal places to be viewed effeciently 
reasonsAHT[('talkTime')] = reasonsAHT[('talkTime')].apply(lambda x: f"{x:.2f}")

# Create the expander for AHT
with st.expander('Check AHT per case'):
    col1, col2, col3 = st.columns([14, 1, 8])  
    
    with col1:
        # Plot the bar chart for talkTime
        fig = px.bar(reasonsAHT, y='talkTime', x='primary_call_reason', template='presentation', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
        
    with col3:
        # Display the DataFrame
        st.dataframe(reasonsAHT, hide_index= True)

#ceate the expander for sentiment
with st.expander('Check sentiment per case'):
    
    #########################
    #   Data
    ##############################

    # crearte DF for all vs WE vs WD call reason vs average sentiment and also Median  
    dfcr = df.groupby(['primary_call_reason']).agg({'average_sentiment':'mean','call_id': 'count'}).reset_index().sort_values(by='average_sentiment')

    dfcrWE = df[df['is_weekend'] == True].groupby('primary_call_reason')['average_sentiment'].mean().reset_index().rename(columns={'average_sentiment': 'average_sentiment_weekend'})

    dfcrWD= df[df['is_weekend'] == False].groupby('primary_call_reason')['average_sentiment'].mean().reset_index().rename(columns={'average_sentiment': 'average_sentiment_weekday'})

    dfcr = dfcr.merge(dfcrWE, on='primary_call_reason', how='left').merge(dfcrWD, on='primary_call_reason', how='left')

    dfcr.sort_values(by='call_id',ascending=False)

    dfcrM= df.groupby(['primary_call_reason']).agg({'average_sentiment':'median'}).reset_index().sort_values(by='average_sentiment').rename(columns={'average_sentiment': 'Median sentiment'})

    dfcr = dfcr.merge(dfcrM, on='primary_call_reason', how='left')
    dfcrHi= dfcr[dfcr['average_sentiment'] < df['average_sentiment'].mean()]
####################################################

    # Chart per median and average sentiment per call reasons 
    fig = px.bar( dfcr,y=['average_sentiment', 'Median sentiment'], x='primary_call_reason',text_auto='.2f',  
    template='presentation',barmode='group', title='Average & Median sentiment per call reasons'.title())
    st.plotly_chart(fig, use_container_width=True)
    
    # Display the data frame and caclulation

    topThree = dfcr['primary_call_reason'].head(3).tolist()

    # Filter the DataFrame to exclude rows in the topFive list
    filtered_df = dfcr[~dfcr['primary_call_reason'].isin(topThree)]

    # Calculate the average for the remaining rows
    overall_average = filtered_df[['average_sentiment', 'Median sentiment']].mean()

    # Display the result for analysis 
    filtered_average = filtered_df['average_sentiment'].mean()
    filtered_median = filtered_df['average_sentiment'].median()
    original_average = df['average_sentiment'].mean()
    original_median = df['average_sentiment'].median()
    AvegVar= filtered_average - original_average
    MedVar=filtered_median - original_median

    # Display the result


    # Custom CSS for styled container
    st.markdown("""
        <style>
        .styled-box {
            background-color: #ffffff; /* White background */
            border: 3px solid #003366; /* Dark blue border */
            border-radius: 10px; /* Rounded corners */
            padding: 20px; /* Internal padding */
            margin-bottom: 20px; /* Space below */
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* Light shadow for depth */
            font-family: 'Arial', sans-serif; /* Professional font */
            transition: transform 0.2s ease, box-shadow 0.2s ease; /* Smooth hover effect */
        }
        .styled-box:hover {
            transform: scale(1.01); /* Slight enlarge on hover */
            box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15); /* Enhanced shadow on hover */
        }
        .styled-header {
            font-size: 22px;
            font-weight: bold;
            color: #003366; /* Dark blue */
            margin-bottom: 15px;
        }
        .styled-paragraph {
            font-size: 16px;
            line-height: 1.6; /* Spacing between lines */
            margin-bottom: 10px;
        }
        .styled-note {
            font-size: 14px;
            font-style: italic;
            color: #555555; /* Subtle gray for notes */
            margin-top: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    
    # HTML structure for the styled box
    content = f"""
    <div class="styled-box">
        <div class="styled-header">Overall Average (excluding Top Three):</div>
        <p class="styled-paragraph">1. Average sentiment will be <strong>{filtered_average:.3f}</strong> instead of <strong>{original_average:.3f}</strong>.</p>
        <p class="styled-paragraph">2. Median sentiment will be <strong>{filtered_median:.3f}</strong> instead of <strong>{original_median:.3f}</strong>.</p>
        <p class="styled-paragraph"><strong>It means that Average will be improved by <span style="color:#003366;">{AvegVar:.3f}</span> and Median by <span style="color:#003366;">{MedVar:.4f}</span>.</strong></p>
        <div class="styled-note">Note: This means that most outliers are related to such calls.</div>
    </div>
    """

    # Display the styled content
    st.markdown(content, unsafe_allow_html=True)

    st.write("Hereunder all call reasons that have more than average sentiment ")
    
    st.dataframe(dfcrHi, hide_index =True)


