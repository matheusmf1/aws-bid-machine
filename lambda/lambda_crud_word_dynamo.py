import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

import uuid

dynamodb = boto3.resource( 'dynamodb' )
table = dynamodb.Table('BidMachineItems')

def putData( event ):
    print('PutData')

    itemId = str(uuid.uuid1())

    try:
        username = event['requestContext']['authorizer']['claims']['cognito:username']
        print( username )

        body = json.loads( event['body'] )

        palavra = body['palavra']

        response = table.put_item(Item= {'ItemId': itemId,'user': username, 'word': palavra})

        print( response['ResponseMetadata']['HTTPStatusCode'] )

        return {
            "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
            "body": json.dumps( response ),
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST"
            }
        }

    except Exception as e:
        return e


def getData( event ):
    print('GetData')

    try:
        username = event['requestContext']['authorizer']['claims']['cognito:username']
        print( f'user {username}')

        response = table.scan( FilterExpression = Attr( 'user' ).eq( username ) & Attr( 'word' ).exists() )
        print( response['Items'] )
        return {
            "statusCode": 200,
            "body": json.dumps( response['Items'] ),
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET"
            }
        }

    except ClientError as e:
        print(e.response['Error']['Message'])


def deleteData( event ):
    print('DeleteData')
    print( event )

    try:
        username = event['requestContext']['authorizer']['claims']['cognito:username']
        print( f'user {username}')
        # username = 'mathew.mfranco-at-gmail.com'
        body = json.loads( event['body'] )
        palavra = body['palavra']

        responseScan = table.scan( FilterExpression = Attr( 'user' ).eq( username ) & Attr( 'word' ).eq( palavra ) )

        scanItem = responseScan['Items'][0]
        print( scanItem )

        response = table.delete_item( Key={'ItemId': scanItem['ItemId']} )

        print( response )

        return {
            "statusCode": 200,
            "body": json.dumps( response ),
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "DELETE"
            }
        }

    except ClientError as e:
        print(e.response['Error']['Message'])



def updateData( event ):
    print('UpdateData')
    print( event )

    try:
        username = event['requestContext']['authorizer']['claims']['cognito:username']
        print( f'user {username}')

        body = json.loads( event['body'] )
        palavra = body['palavra']
        novaPalavra = body['novaPalavra']

        responseScan = table.scan( FilterExpression = Attr( 'user' ).eq( username ) & Attr( 'word' ).eq( palavra ) )

        scanItem = responseScan['Items'][0]
        print( scanItem )

        response = table.update_item(
            Key={'ItemId': scanItem['ItemId']},
            UpdateExpression = 'SET word = :newWord',
            ExpressionAttributeValues = { ':newWord': novaPalavra }
        )

        print( response )

        return {
            "statusCode": 200,
            "body": json.dumps( response ),
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "PUT"
            }
        }

    except ClientError as e:
        print(e.response['Error']['Message'])



def lambda_handler(event, context):

    if event['httpMethod'] == 'POST':
        return putData( event )

    elif event['httpMethod'] == 'GET':
        return getData( event )

    elif event['httpMethod'] == 'DELETE':
        return deleteData( event )

    elif event['httpMethod'] == 'PUT':
        return updateData( event )