import json
import boto3

client = boto3.client('ses', 
                  aws_access_key_id="#############",
                  aws_secret_access_key="#####################",
                  region_name="us-east-2")

def lambda_handler(event, context):
    # Get the file URL and email address from the event
    file_url = event['file_url']
    email = event['email']

    # send email
    response = client.send_email(
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': f'Your file has be uploaded and here your URL {file_url}'
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': f'File uploaded. URL: {file_url}'
            },
        },
        Source = 'bhanuvardhanreddyg@gmail.com'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully')
    }