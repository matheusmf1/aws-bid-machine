import json
import boto3

def lambda_handler(event, context):
	print( event )
	
	bucketName = event['requestPayload']['Records'][0]['s3']['bucket']['name']
	
	fileName = event['requestPayload']['Records'][0]['s3']['object']['key']
	
	originfolder = fileName.split("/")[0]
	file = fileName.split("/")[1]
	
	key = file.split(".xml")[0]
	key += ".json"
	
	body = json.dumps( event['responsePayload'] )
	
	destinationFolder = 'JSON/'
	
	client = boto3.client('s3')
	
	print(body)
	
	client.put_object( Body = body, Bucket = bucketName , Key = destinationFolder + key )
	print("Uploaded to S3")