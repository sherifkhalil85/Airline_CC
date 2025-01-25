import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns


# Configure page
st.set_page_config(
    layout='wide', page_title='Air Line - Sentiment Analysis', page_icon=':airplane_departure:'
)


# Load data
df = pd.read_csv('data/aggregated2.csv')
###############################################
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

########################################
#grouping daily sentiment average and make daily dataframe

dfs = df.groupby(['transaction_date', 'is_weekend']).agg({'call_id':'count',
    'average_sentiment': [
        'mean', 
        'median', 
        lambda x: x.quantile(0.75),  # 75th percentile (Q3)
        lambda x: x.quantile(0.25)   # 25th percentile (Q1)
    ]
}).reset_index()

dfs.columns = ['transaction_date', 'is_weekend','Calls', 'average_sentiment', 'median', 'Q3', 'Q1']
dfs['formatted_sentiment'] = dfs['average_sentiment'].apply(lambda x: f"{x:.3f}")
dfs['IQR'] = dfs['Q3'] - dfs['Q1']
dfs['UL']= dfs['Q3'] + (1.5*dfs['IQR'] )
dfs['LL']= dfs['Q1'] - (1.5*dfs['IQR'] )

#create draft DF to calculate each record :
df_merged = df.merge(dfs[['transaction_date', 'is_weekend', 'UL', 'LL']], on=['transaction_date', 'is_weekend'], how='left')

# start calulate each record individually  
df_merged['above_UL'] = df_merged['average_sentiment'] > df_merged['UL'] 
df_merged['below_LL'] = df_merged['average_sentiment'] < df_merged['LL']

# sum all outliers per each day 
outliers_count = df_merged.groupby('transaction_date').agg({
    'above_UL': 'sum',  # Sum of True values gives the count of records above UL
    'below_LL': 'sum'   # Sum of True values gives the count of records below LL
}).reset_index()

# return the calculted outliers per each day to our daily dataframe
dfs = pd.merge(dfs, outliers_count, on='transaction_date', how='left')

# add latest calculated fields to sum all outliers
dfs['Outliers'] = dfs['above_UL'] + dfs['below_LL']
dfs['Outliers%'] = (dfs['Outliers'] / dfs['Calls'])*100


##############################################
# Calculation to be used in metrics
Totalcalls = dfs['Calls'].sum()
overall_average_sentiment = f"{df['average_sentiment'].mean():.3f}"
total_OutliersPercent = f"{((dfs['Outliers'].sum() / Totalcalls)*100):.2f}%"

Average_Weekend =  f"{df['average_sentiment'][df['is_weekend']== True ].mean():.3f}"
Average_Weekday =  f"{df['average_sentiment'][df['is_weekend']== False ].mean():.3f}"

total_OutliersWE  = f"{((dfs['Outliers'][dfs['is_weekend']== True ].sum() / dfs['Calls'][dfs['is_weekend']== True ].sum())*100):.2f}%"
total_OutliersWD = f"{((dfs['Outliers'][dfs['is_weekend']== False ].sum() / dfs['Calls'][dfs['is_weekend']== False].sum())*100):.2f}%"

# measure delta 
Weekend_delta = f"{float(Average_Weekend) - float(overall_average_sentiment):.3f}"
Weekday_delta = f"{float(Average_Weekday) - float(overall_average_sentiment):.3f}"


# Measure delta for Outliers percentage

Weekend_delta_outliers =f"{float(total_OutliersPercent.strip('%')) -  float(total_OutliersWE.strip('%')):.2f}%"
Weekday_delta_outliers =f"{float(total_OutliersPercent.strip('%')) -  float(total_OutliersWD.strip('%')):.2f}%"


###########################################



image_url = "https://media.istockphoto.com/id/1254541032/photo/angry-woman-calling-arguing-on-phone-at-home.jpg?s=2048x2048&w=is&k=20&c=ycdaGtU1kj8xSvIaYwSdxBToaabARO3x-J2J8CLLbOQ="



################################################
# metrics
col1,col2,col3,col4 = st.columns(4)

with col1:

    st.metric('Overall Average Sentiment',overall_average_sentiment)
    st.metric('Outliers%',total_OutliersPercent)

with col2:
    
    st.metric('Overall Weekdays Sentiment',Average_Weekday , delta= Weekday_delta)
    st.metric("weekdays Outliers %", total_OutliersWD, delta = Weekday_delta_outliers)

   
with col3:
    st.metric('Overall Weekends Sentiment',Average_Weekend , delta= Weekend_delta)
    st.metric("weekend Outliers %",total_OutliersWE , delta= Weekend_delta_outliers)




with col4: # Display the image

    st.image(image_url,  use_column_width=True)

#############################################
### create pages to explain and understand sentiment pattern
st.markdown(
    """
    <style>
    /* Overall tab container styling */
    .stTabs [role="tablist"] {
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 8px;
    }

    /* Unselected tab styling */
    .stTabs [role="tab"] {
        color: #555;
        font-size: 16px;
        font-weight: 500;
        padding: 10px 20px;
        border-radius: 5px 5px 0 0;
        background-color: #f9f9f9;
    }

    /* Hover effect on tabs */
    .stTabs [role="tab"]:hover {
        background-color: #DBE2E9;
    }

    /* Active tab styling */
    .stTabs [aria-selected="true"] {
        color: #fff;
        background-color: #4B68B8;
        font-weight: bold;
        border-bottom: 3px solid #0827F5;
    }
    </style>
    """,unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5=st.tabs(['Overall distribution','Daily average sentiment trend','Daily sentiment distribution','Tones view','Final conclusion'])
#########################################  

with tab1:# histograms
    histogram_choice = st.selectbox("Choose Histogram View:",['By Sentiment Category', 'By Weekend Status'])

# Conditional based on selection
    if histogram_choice == 'By Sentiment Category':
        fig = px.histogram(df, x='average_sentiment', color='sentiment_category', marginal='box',
         template='presentation',title= histogram_choice)
    else:
        fig = px.histogram(df, x='average_sentiment', color='is_weekend', marginal='box',
         template='presentation', title= histogram_choice)

# Display the selected histogram
    st.plotly_chart(fig, use_container_width=True)
    

with tab2: # time series trend to illustrates Daily average sentiment trend.

    # Create the base line trace with all data points // Note : can not correctly highlight weekends in daily trends with regular px.line
    fig = go.Figure()

    fig.add_trace(go.Scatter(  
        x=dfs['transaction_date'],
        y=dfs['average_sentiment'],
        mode='lines+markers+text',  # Add lines, markers, and text
        text=dfs['formatted_sentiment'],  # Use formatted sentiment as text labels
        textposition='top center',  #
        name='Average Sentiment',
        line=dict(color='blue'),
        showlegend=True
        ))

    # Filter out the weekend data points for highlighting
    weekend_data = dfs[dfs['is_weekend'] == True]

    fig.add_trace(go.Scatter(
        x=weekend_data['transaction_date'],
        y=weekend_data['average_sentiment'],
        mode='markers', 
        
        textposition='top center', 
        name='Weekend',
        marker=dict(color='red', size=10),
        showlegend=True
        ))

    # Update layout for better readability
    fig.update_layout(
        title='Average Sentiment Over Time',
        xaxis_title='Transaction Date',
        yaxis_title='Daily Average Sentiment',
        legend_title='Legend',
        template='simple_white' 
        )

        
    #######################
    st.plotly_chart(fig,use_container_width=True)

with tab3: #whisekr boxplot on daily basis
    fig=px.box(df,y='average_sentiment',x='transaction_date',template='presentation',color='is_weekend',title='Daily Sentiment')
    st.plotly_chart(fig,use_container_width=True)

    # Display the DataFrame to illustartes the outliers daily 
    dfs1 = dfs.drop(columns=dfs.columns[5:11])

    st.markdown(
    """
    <style>
        .streamlit-container {
            display: flex;
            justify-content: center;
        }
        .dataframe {
            width: 1200px;  /* Adjust width here */
        }
    </style>
    """,
    unsafe_allow_html=True)

    st.dataframe(dfs1, hide_index=True,width=1200)  

    
#####################################
with tab4: # Tones 
    
    # Pivot for both agent and customer to show counts
    pivot_df2= df.pivot_table(values='call_id', index='customer_tone', columns='agent_tone', aggfunc='count')
    pivot_df_reset2= pivot_df2.reset_index().melt(id_vars='customer_tone', var_name='agent_tone', value_name='call_id')
    
    
    # customer tone
    cst_sen = df.groupby('customer_tone')['average_sentiment'].mean().reset_index().sort_values(by= 'average_sentiment', ascending=False)
    cst_sen['average_sentiment'] = cst_sen['average_sentiment'].apply(lambda x: f"{x:.4f}")

    

    # Agent tone 
    agent_sen= df.groupby('agent_tone')['average_sentiment'].mean().reset_index().sort_values(by= 'average_sentiment', ascending=False)
    agent_sen['average_sentiment'] = agent_sen['average_sentiment'].apply(lambda x: f"{x:.4f}")

    # Pivot the DataFrame to create a matrix for the heatmap
    pivot_df = df.pivot_table(values='average_sentiment', index='customer_tone', columns='agent_tone', aggfunc='mean')
    
    # dataframe to build stacked columns chart
    pivot_df_reset = pivot_df.reset_index().melt(id_vars='customer_tone', var_name='agent_tone', value_name='average_sentiment')

    

  
  # showing dataframe to compare between sentiment based on agent and custmer and vs each other
    col1,col2,col3 = st.columns(3)
    
    with col1:
        st.dataframe(cst_sen,hide_index=True)
    with col2:
        st.dataframe(agent_sen, hide_index=True)
    with col3:
        st.dataframe(pivot_df)

        


# stacked column to depict the impact on Average sentiment per agent and customer

# color map to unify the view 
    custom_colors = ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#1a9850']
 

    selectionT = st.selectbox("Choose View:",['Volumes','Average sentiment for agent & customer tone','Heatmap for agent and customer'])

    if selectionT == 'Volumes':
        fig = px.bar(
            pivot_df_reset2,
            x='agent_tone',
            y='call_id',
            color='customer_tone',
            barmode='stack',
            template='presentation',
            text_auto=True,
            color_discrete_map={
                '1 angry': '#d73027',
                '2 frustrated': '#fc8d59',
                '3 neutral': '#fee08b',
                '4 calm': '#d9ef8b',
                '5 polite': '#1a9850'
            },
            title="Relationship Between Agent Tone and Customer Tone"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif selectionT == 'Average sentiment for agent & customer tone':
        # stacked graph 
        fig= px.bar(
            pivot_df_reset,
            x='agent_tone',
            y='average_sentiment',
            color='customer_tone',
            barmode='stack',
            template='presentation',
            text='average_sentiment',
            color_discrete_sequence=custom_colors,
            title="Relationship Between Agent Tone and Customer Tone (Sentiment)",
            )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='inside')  # Format the text
        st.plotly_chart(fig,use_container_width=True)


    # Seaborn Heatmap with Moderately Reduced Figure Size
    elif selectionT == 'Heatmap for agent and customer':
        plt.figure(figsize=(5, 3.5))  # Moderately reduced figure size
        sns.heatmap(pivot_df, annot=True, fmt=".2f",
                    cmap="RdYlGn",  # Color scheme
                    cbar=True,  # Show color bar
                    annot_kws={"size": 8},  # Adjust annotation font size
                    linewidths=0.1)
        plt.title('Heatmap of Average Sentiment by Customer and Agent Tone', fontsize=12)  # Adjust title font size
        plt.xlabel('Agent Tone', fontsize=10)  # Adjust x-axis label font size
        plt.ylabel('Customer Tone', fontsize=10)  # Adjust y-axis label font size
        plt.tick_params(axis='both', which='major', labelsize=8)  # Adjust font size for axis ticks
        plt.tight_layout()  # Automatically adjust layout to avoid clipping
        st.pyplot(plt)



    ############################

with tab5: # final conclusion
    
    dftt = df.groupby(['customer_tone','is_weekend']).agg({'call_id': 'count','talkTime': 'mean', 'waitingTime': 'mean'}).reset_index()

    # Custom CSS for conclusion box with a paper-like background and border
    st.markdown("""
        <style>
        .conclusion-box {
            background-color: #ffffff;
            border-radius: 10px;
            border: 2px solid #2196F3;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .conclusion-box h1 {
            font-size: 24px;
            color: #2196F3;
        }
        .conclusion-box p {
            font-size: 16px;
            color: #333;
        }
        .info-icon {
            color: #2196F3;
            font-size: 32px;
            vertical-align: middle;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display the conclusion section with a paper-like background and info icon
    st.markdown(f"""
        <div class="conclusion-box">
            <h1><i class="info-icon">ℹ️</i> Conclusion after analyzing {df.shape[0]} calls:</h1>
            <p>1. There are rush hours and seasonality in weekends more than regular business days 
            ({(df[df['is_weekend'] == True].shape[0] / df.shape[0]) * 100:.2f}% of samples in weekends).</p>
            <p>2. Talk time and waiting have no impact on customer tone
            , either on weekends or business days.</p>
            <p>3. there are a weak relation between Talk time and average sentiment on daily level but overall logs no relations</p>
            <p>4. As we see impact on sentiment related to business days or weekends not significant .</p>
            <p>5. As we mentioned before, call reasons may have a negative impact, especially the top 3.</p>
            <p>6. For customer tones and agent tones, it was clearly observed that the agent's tone drives the average sentiment, 
            even if the customer is angry or frustrated.</p>
        </div>
    """, unsafe_allow_html=True)

    # create checkbox to show the df of TT vs sentiment
    if st.checkbox("Show Talk Time Details with customer tone", value=False):
        # Display the dataframe with talk time details
        st.dataframe(dftt, hide_index=True)


    # Soultion 
    

    # Custom CSS to create a paper-like background with border
    st.markdown("""
        <style>
        .recommendation-box {
            background-color: #f4f4f9;
            border-radius: 10px;
            border: 2px solid #4CAF50;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        }
        .recommendation-box h1 {
            font-size: 24px;
            color: #4CAF50;
        }
        .recommendation-box p {
            font-size: 16px;
            color: #333;
        }
        .success-icon {
            color: #4CAF50;
            font-size: 32px;
            vertical-align: middle;
        }
        </style>
    """, unsafe_allow_html=True)

    # Display the recommendations section with a paper-like background and a success icon
    st.markdown("""
    <div class="recommendation-box" style="padding-left: 20px;">
        <h1><i class="success-icon" style="color: green;">✔️</i> Recommendations to Improve Sentiment:</h1>
        <p>1. Provide targeted training to agents to maintain calmness and professionalism during calls.</p>
        <p>2. Prioritize training on the top three call reasons, with a specific focus on IRROPS (Irregular Operations). 
        This will enhance product knowledge, boost agent confidence, and improve tone during interactions.</p>
        <p>3. Empower agents to offer compensation in cases related to IRROPS, ensuring customers feel valued and supported.</p>
        <p>Expected Outcomes:</p>
        <ul style="margin-left: 20px;">
            <li>Agents will handle calls with greater calmness, professionalism, and confidence, enabling them to provide 
            solutions or compensation effectively.</li>
            <li>Reduced talk time, leading to shorter customer wait times, even during high-demand periods like weekends.</li>
            <li>A noticeable improvement in customer sentiment, shifting from negative to at least neutral or positive.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    

