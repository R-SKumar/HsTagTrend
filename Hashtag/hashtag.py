import streamlit as st
import pandas as pd
from datetime import datetime
import boto3
import json
import pytz
import matplotlib.pyplot as plt

# AWS configuration
AWS_REGION = 'xxx'
AWS_ACCESS_KEY_ID = 'xxx'
AWS_SECRET_ACCESS_KEY = 'xxx'
LAMBDA_FUNCTION_NAME = 'lamdaFunction'
DYNAMODB_TABLE_NAME = 'dynamodbtable'

# Initialize boto3 clients with credentials
lambda_client = boto3.client(
    'lambda',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

dynamodb_client = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

table_raw = dynamodb_client.Table('dynamodbtable1')
table_hastag = dynamodb_client.Table('dynamodbtable1')

def getdynamodb(table):
    response = table.scan()
    posts = response.get('Items', [])
    try:    
        # Sort posts in descending order by timestamp
        posts.sort(key=lambda x: x['Timestamp'], reverse=True)    
    except:
        err = ""
    return posts

def updateinheader(posts):
    # st.header("All Posts")    
    for post in posts:
        st.subheader(post['User'])
        st.write(post['Post'])
        st.caption(post['Timestamp'])
        st.markdown("---")

def gettophashtagschart(hashtags):
    # Get top 5 hashtags or fewer if there are not enough
    top_hashtags = hashtags[:5]
    df_top_hashtags = pd.DataFrame(top_hashtags)    
    st.subheader("Top Hashtags")    
    if not df_top_hashtags.empty:
        fig, ax = plt.subplots()        
        # Plot line chart
        ax.plot(df_top_hashtags['hashtag'], df_top_hashtags['count'], marker='o')        
        # Add labels for each point
        for i, row in df_top_hashtags.iterrows():
            ax.text(row['hashtag'], row['count'], str(row['count']), fontsize=17, ha='right')        
        # Set titles and labels
        ax.set_xlabel('Hashtags')
        ax.set_ylabel('Count')
        ax.set_title('Top Hashtags Count')        
        # Display the plot
        st.pyplot(fig)
    else:
        st.write("No hashtags data available to display.")    

def allhashtagsinfo(hashtags):
    df = pd.DataFrame(hashtags)    
    # Display the count of hashtags in the subheader
    num_hashtags = len(df)
    if num_hashtags > 0 :
        st.subheader(f"Hashtags ({num_hashtags})")    
        st.dataframe(df,height=250)

# Streamlit interface
st.sidebar.title("Post Composition")

if st.sidebar.button("Show Trending Hashtags"):    
    # Fetch and display hashtags
    hashtags = getdynamodb(table_hastag)    
    # Create 3 columns for layout
    col1, col2,col3 = st.columns(3)    
    with col1:
        gettophashtagschart(hashtags)    
    with col3:
        allhashtagsinfo(hashtags)

st.header("All Posts")
st.sidebar.write("Compose a New Post")

# Input fields in the sidebar
username = st.sidebar.text_input("Username")
post_content = st.sidebar.text_area("Write your post here", height=120)

# Initialize a placeholder for status messages
status_placeholder = st.sidebar.empty()

# Button to submit the post
if st.sidebar.button("Post"): 
    status_placeholder = st.sidebar.empty()
    if username and post_content:
        # Create a timestamp with timezone info
        timestamp = datetime.now(pytz.utc).isoformat()
        # Send post content to AWS Lambda
        try:
            payload = {
                'post_content': {
                    'User': username,
                    'Timestamp': timestamp,
                    'Post': post_content
                }
            }
            # print(payload)
            response = lambda_client.invoke(
                FunctionName=LAMBDA_FUNCTION_NAME,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            # print('\n',response)
            response_payload = json.loads(response['Payload'].read().decode('utf-8'))
            # print('\n',response_payload)
            if response_payload['statusCode'] == 200:                
                status_placeholder.success("Post submitted successfully!")                
            else:
                status_placeholder.error(f"Failed to submit post: {response_payload.get('body')}")
        except Exception as e:
            status_placeholder.error(f"An error occurred: {e}")
    else:
        status_placeholder.error("Please provide both username and content.")

# Fetch and display posts from DynamoDB
posts = getdynamodb(table_raw)
if len(posts) > 0 :
    updateinheader(posts)
else:
    st.write('No posts have occurred so far.')




