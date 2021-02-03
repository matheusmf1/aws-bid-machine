import json
import boto3 
import awswrangler as wr
import pandas as pd
import os

from collections import Counter
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr


def getUserWords():
  print('GetUserWords')
    
  try:

    tableName = os.environ[ 'dynamoDbTable' ]
    
    dynamodb = boto3.resource( 'dynamodb' )
    table = dynamodb.Table( tableName )
      
    response = table.scan( FilterExpression = Attr( 'word' ).exists() )
    data = response['Items']
    
    users = { }
    
    for user in data:
      users[ user['user'] ] = list( map( lambda srt: srt.lower(), user['word'] ) )
      
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


def getAdditionalEmailInfo( df ):

  data = { 'orgao': [], 'linkEdital': [], 'objeto': [] }

  for row in df['orgao']:
    data['orgao'].append( row )

  for row in df['links']:
    data['linkEdital'].append( row )
    
  for row in df['objeto']:
    data['objeto'].append( row )

  return data


def getLicitacaoObject( df ):
  
  print( df['objeto'] )
  
  for row in df['objeto']:
    print( row )
  
  
def sendNotification( event, dictFoundWords, additionalEmailInfo ):
  
  print( 'SendNotification' )
  ses = boto3.client( 'ses' )
  
  fileName = event['requestPayload']['Records'][0]['s3']['object']['key']
  
  fileName = fileName.split( 'JSON/' )[1].split( '.json' )[0] + '.xml'
  print(fileName)
  
  for user in dictFoundWords:
    
    email = user.replace( '-at-', '@' )
    
    emailName  = email.split('@')[0]
    
    wordsCounter = Counter( dictFoundWords[user] ).items()
    
    orgaoLicitanteCounter = Counter( additionalEmailInfo['orgao'] ).items()
    
    words = ''
    orgaoLicitante = ''
    linkEdital = ''
    objeto = ''
    
    for item in wordsCounter:
      words += f'<li>{ item[0] }: { item[1] } vez(es).</li>'
      
    for orgao in orgaoLicitanteCounter:
      orgaoLicitante += f'<li>{ orgao[0] }: { orgao[1] } vez(es).</li>'
      
      
    for link in additionalEmailInfo['linkEdital']:
      linkEdital += f'<li>{ link }</li>'

    for obj in additionalEmailInfo['objeto']:
      objeto += f'<li>{ ojb }</li>'
      
      
    bodyHtml = f"""<!DOCTYPE html>
    <html lang="pt-BR">
    
    <h1>Olá {emailName}</h1>
    
    <p>Esse email contém as informações geradas de forma automática e podem ser localizadas no arquivo <b>{ fileName }</b></p>
    
    <h4>Aqui estão as palavras encontradas:</h4>
    <ul>
     { words }
    </ul>
    
    <h4>Órgão Licitante:</h4>
    <ul>
      { orgaoLicitante }
    </ul>

    <h4>Objeto da Licitação:</h4>
    <ul>
      { objeto }
    </ul>
    
    <h4>Link do Edital:</h4>
    <ul>
      { linkEdital }
    </ul>
    
    </html>
"""
    
  
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
          'Html': {
            'Data': bodyHtml,
            'Charset': 'UTF-8'
          }
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
  
  additionalEmailInfo = getAdditionalEmailInfo( df )
  
  sendNotification( event, foundWordUsers, additionalEmailInfo )
  
  print('ACABOU')