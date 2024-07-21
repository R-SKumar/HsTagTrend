# Hashtag Trend
Hashtag Trend Analyzer Project for study purpose.

we aim to develop a Streamlit application that allows users to compose and publish posts, similer as popular social media platforms. This application will integrate with AWS Lambda and DynamoDB to facilitate post processing and hashtag analysis

## Technologies : 
Python, AWS(Lambda, DynamoDB) and Streamlit

## Libraries To Install:
    pip install pandas
    pip install boto3
    pip install matplotlib
    pip install streamlit

## Other Library:
json, datetime, timezone and regex

## Running the Application:    
    streamlit run [py fileanme with extension]

## ASW configuration
  * Create AWS account
  * Create IAM user and add Permissions policies
    - Create access key
    - AmazonDynamoDBFullAccess
    - AWSLambda_FullAccess
    - AWSLambdaDynamoDBExecutionRole
    - AWSLambdaInvocation-DynamoDB
    - Inline policy if required Inline.txt
  * Create Lamda function
    - Add code from lamdacode.py  
  * Create DynamoDB table
    - 2 tables
