import json
import boto3 
import awswrangler as wr
import pandas as pd

from collections import Counter
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


def getUserWords():
  print('GetUserWords')
    
  try:
    
    dynamodb = boto3.resource( 'dynamodb' )
    table = dynamodb.Table('BidMachineItems')
      
    response = table.scan( FilterExpression = Attr( 'word' ).exists() )
    data = response['Items']
    
    users = { }
    
    for user in data:
      users[ user['user'] ] = []
      
    for userWord in data:
      users[ userWord['user'] ].append( userWord['word'].lower() )
      
    print( users )
    
    return users
      
  except ClientError as e:
      print(e.response['Error']['Message'])


def searchUserWords( users, df ):
  print('SearchUserWords')
  
  foundWordUsers = {}
  
  for key in users:
    foundWords = []
    
    for row in df['palavraEncontrada']:
      
      for word in row:
        if word in users[key]:
          foundWords.append( word.capitalize() )
          foundWordUsers[ key ] = foundWords

  return foundWordUsers


def sendNotification( event, dictFoundWords ):
  
  print( 'SendNotification' )
  ses = boto3.client( 'ses' )
  
  fileName = event['requestPayload']['Records'][0]['s3']['object']['key']
  
  fileName = fileName.split( 'JSON/' )[1].split( '.json' )[0] + '.xml'
  print(fileName)
  
  for content in dictFoundWords:
    
    email = content.replace( '-at-', '@' )
    
    emailName  = email.split('@')[0]
    
    wordsCounter = Counter( dictFoundWords[content] ).items()
    
    words = ''
    
    for item in wordsCounter:
      words += f'\n{ item[0] }: { item[1] } vez(es).'
      
    body = f"""
      \nOlá {emailName}, esse email contém as informações geradas de forma automática e podem ser localizadas no arquivo { fileName }
      
      \nAqui estão as palavras encontradas:
      { words }
  
  """

    print( body )
  
    ses.send_email(
      Source = "matmfran@amazon.com",
      
      Destination = {
        'ToAddresses': [email],
        'CcAddresses': ['matmfran@amazon.com'],
      },
      
      ReplyToAddresses = [ 'matmfran@amazon.com' ],
      
      Message = {
        'Subject': {
          'Data': 'Bid Machine Notification',
          'Charset': 'UTF-8'
        },
        'Body': {
          'Text': {
            'Data': body,
            'Charset': 'UTF-8'
          },
          # 'Html': {
          #   'Data': body,
          #   'Charset': 'UTF-8'
          # }
        }
      }
  
    )




def lambda_handler(event, context):
  
  print( event )

  body = event['responsePayload']['body']
    
  df = pd.read_json( body )
  
  df['palavraEncontrada'] = df['palavraEncontrada'].map( lambda x: x.lower().split(',') )
  
  users = getUserWords()
  
  foundWordUsers = searchUserWords( users, df )
  
  print( foundWordUsers )
  
  sendNotification( event, foundWordUsers )
  
  print('ACABOU')