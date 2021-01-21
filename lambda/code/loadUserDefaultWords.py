import json
import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

import uuid

dynamodb = boto3.resource( 'dynamodb' )
table = dynamodb.Table('BidMachineItems')

def lambda_handler(event, context):
    
    body = json.loads( event['body']  )
    
    email = body['email']
    
    email = email.replace( '@', '-at-' )
    
    itemId = str(uuid.uuid1())
    
    palavra = [ "AWS","Amazon","Web Service","Oracle","Microsoft",
    "Azure","Windows","Google","Nuvem","Cloud","VMWare","IBM",
    "Backup","Huawei","banco de dados","servidor","virtualizacao",
    "servico","computacao","computacao em nuvem","infraestrutura como servico",
    "plataforma como servico","Software","Hardware","Tecnologia","Linux","trafego de rede",
    "maquina virtual","Web Application","Web Server","Firewall","VPN","SQL","MySQL",
    "PostgreSQL","Container","kubernetes","Analytics","IOT" ]
    
    palavra.sort()
    
    try:
        
        response = table.put_item(Item= {'ItemId': itemId,'user': email, 'word': palavra})
        
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
        print( e )
        
        return {
            "statusCode": response['ResponseMetadata']['HTTPStatusCode'],
            "body": json.dumps( response ),
            "headers": {
                "Access-Control-Allow-Headers" : "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST"
            }
        }