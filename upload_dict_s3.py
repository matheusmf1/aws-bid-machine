import json
import boto3

def lambda_handler(event, context):

  fileName = event['requestPayload']['Records'][0]['s3']['object']['key']
    
  originfolder = fileName.split("/")[0]
  file = fileName.split("/")[1]

  key = file.split(".xml")[0]
  key += ".json"

  body = event['responsePayload']
  body2 = bytes( json.dumps(body).encode('UTF-8'))

  destinationFolder = 'JSON/'

  client = boto3.client('s3')

  print( body2 )
  print('Before upload')
  client.put_object( Body = body2, Bucket = "rhs-xml-test", Key = destinationFolder + key )
  print('Foooi')