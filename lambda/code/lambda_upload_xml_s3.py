import json
import base64
import boto3
import os

def lambda_handler(event, context):
    
    body = base64.b64decode( event['body'] )
    
    decodedBody = body.decode( 'ISO-8859-1' )
   
    xmlStart = decodedBody.find( '<licitacoes>' )
    xmlEnd = decodedBody.find( '</licitacoes>' )
    
    file = decodedBody[ xmlStart: xmlEnd + 13 ]

    print( file )
    
    fileNameStart = decodedBody.find( 'filename=' )
    fileNameEnd = decodedBody.find( '.xml' )

    name = decodedBody[ fileNameStart: fileNameEnd ] + '.xml"'
    
    temp = name.split( '=' )
    fileName = temp[1].split( '"' )[1]
    
    destinationFolder = 'XML/'
    bucketName = os.environ[ 'bucketData' ]
    
    client = boto3.client('s3')
    
    response = client.put_object( Body = file, Bucket = bucketName , Key = destinationFolder + fileName )
    print("Uploaded to S3")
    
    return {
        "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
        "body": json.dumps( response ),
        "headers": {
            "Access-Control-Allow-Headers" : "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
        }
    }