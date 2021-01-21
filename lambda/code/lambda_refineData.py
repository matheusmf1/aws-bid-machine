import json
import boto3 
import awswrangler as wr
import pandas as pd
import numpy as np


def getJsonDataWr( event ):
	
	bucket = 's3://rhs-xml-test/'
	filePath = event['Records'][0]['s3']['object']['key']
	path = f'{bucket}{filePath}'
	
	return wr.s3.read_json( [ path ] )	
	
	
def createNewColumns( df ):
	print( "CreateNewColumns" )
	
	try:
		
		if type( df['palavrasEncontradasAgrupadasXml']['palavra'] ) == str:
			
			df['palavraEncontrada'] = df['palavrasEncontradasAgrupadasXml']['palavra']
			
		elif type(df['palavrasEncontradasAgrupadasXml']['palavra']) == list:
			
			df['palavraEncontrada'] = ",".join( df['palavrasEncontradasAgrupadasXml']['palavra'] )
		
		elif type(df['palavrasEncontradasAgrupadasXml']['palavra']) == np.float64:
			df['palavraEncontrada'] = "Palavras não encontradas no XML."
			
		
		if type( df['linksAgrupadosXml']['link'] ) == str:
			
			df['links'] = df['linksAgrupadosXml']['link']
			
		elif ( type( df['linksAgrupadosXml']['link'] ) == list ):
			
			df['links'] = ",".join( df['linksAgrupadosXml']['link'] )
			
		elif type( df['linksAgrupadosXml']['link'] ) == np.float64:
			df['links'] = "Não foi encontrato nenhum link no XML."
			
		
		if type( df['trechosEncontradosAgrupadosXml']['trecho'] ) == str:
			
			df['trechos'] = df['trechosEncontradosAgrupadosXml']['trecho']
			
		elif ( type( df['trechosEncontradosAgrupadosXml']['trecho'] ) == list ):
			
			df['trechos'] = ",".join( df['trechosEncontradosAgrupadosXml']['trecho'] )
			
		elif type( df['trechosEncontradosAgrupadosXml']['trecho'] ) == np.float64:
			df['trechos'] = "Não foi encontrado nenhum trecho no XML."
	
	except Exception as e:
		print('Deu ruim: ' + e)


def prepareDataSet( data ):
	
	print( 'PrepareDataSet' )
	
	if data[ 'linksAgrupadosXml' ] is None:
		data['linksAgrupadosXml'] = { 'link': None }
		
	if data[ 'palavrasEncontradasAgrupadasXml' ] is None:
		data['palavrasEncontradasAgrupadasXml'] = { 'palavra': None }
	
	if data[ 'trechosEncontradosAgrupadosXml' ] is None:
		data['trechosEncontradosAgrupadosXml'] = { 'trechos': None }
		
	df = pd.DataFrame( data )
	
	# Create new Columns
	createNewColumns( df )

	# Drop nested columns
	df.drop( ['palavrasEncontradasAgrupadasXml', 'linksAgrupadosXml', 'trechosEncontradosAgrupadosXml' ], axis = 1, inplace = True  )
	
	df.reset_index( drop = True, inplace = True )
	df.drop_duplicates( inplace = True )

	return df

def save_to_s3_parquet( df ):
	
	path = 's3://rhs-xml-test/refined_data/'

	wr.s3.to_parquet(
		df = df,
		path = path,
		dataset = True,
		mode = "append"
	)

	
def lambda_handler( event, context ):
	
	data = getJsonDataWr( event )
	
	licitacaoType = type(data['licitacoes']['licitacao'])
	
	if licitacaoType == dict:
		
		print( 'licitacaoType dict' )
		
		mainData = data['licitacoes']['licitacao']
		df_new = prepareDataSet( mainData )
		
	elif licitacaoType == list:
		
		print( 'licitacaoType list' )
		df_new = pd.DataFrame()
		
		for licitacao in data['licitacoes']['licitacao']:
			df_new = df_new.append( prepareDataSet( licitacao ), ignore_index = True )
			

	save_to_s3_parquet( df_new )
	print( 'File uploaded to S3 as parquet' )
	
	return {'body': df_new.to_json() }