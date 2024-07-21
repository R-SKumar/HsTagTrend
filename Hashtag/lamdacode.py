import json
import boto3
import re
from datetime import datetime

AWS_REGION = 'xxx'
AWS_ACCESS_KEY_ID = 'xxx'
AWS_SECRET_ACCESS_KEY = 'xxx'

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name= AWS_REGION
)

dynamodb = session.resource('dynamodb')
table_raw = dynamodb.Table('dynamodbtable1')
table_hastag = dynamodb.Table('dynamodbtable2')

def lambda_handler(event, context):
    try:        
        # print(f"Received event: {json.dumps(event)}")        
        post_content = event.get('post_content', {})
        
        if not post_content:
            raise ValueError("No post content found")
        
        # Ensure required keys are present
        user = post_content.get('User')
        post = post_content.get('Post')
        timestamp = post_content.get('Timestamp')
        
        if not user or not post or not timestamp:
            raise ValueError("Missing required fields in post content")
            
        # Post to posttable with Partition key and Sort key
        table_raw.put_item(
            Item={
                'User': str(user),
                'Timestamp': str(timestamp),
                'Post': str(post)
            }
        )
        
        # Extract hashtags and clean up post content
        if isinstance(post, str):
            hashtags = re.findall(r'#\w+', post)
            post_text = re.sub(r'#\w+', '', post).strip()
            
            # Store hashtags in DynamoDB
            for hashtag in hashtags:            
                table_hastag.update_item(
                    Key={'hashtag': hashtag},
                    UpdateExpression="ADD #count :inc",
                    ExpressionAttributeNames={'#count': 'count'},
                    ExpressionAttributeValues={':inc': 1}
                )
        else:
            raise TypeError("Post content should be a string")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Post processed successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error processing post ','inputmsg' : str(post_content), 'error': str(e)})
        }