import json
import boto3 
import awswrangler as wr
import pandas as pd


def getJsonDataWr( event ):
	
	bucket = 's3://rhs-xml-test/'
	filePath = event['Records'][0]['s3']['object']['key']
	# filePath = 'JSON/155917_3_1091_20201207220101.json'
	# filePath = "JSON/155917_8_1095_20201207223020.json"
	
	path = f'{bucket}{filePath}'
	
	return wr.s3.read_json( [ path ] )	
	
	
def createNewColumns( df ):
	
	try:
		
		if type( df['palavrasEncontradasAgrupadasXml']['palavra'] ) == str:
			
			df['palavraEncontrada'] = df['palavrasEncontradasAgrupadasXml']['palavra']
			
		elif type(df['palavrasEncontradasAgrupadasXml']['palavra']) == list:
			
			df['palavraEncontrada'] = ",".join( df['palavrasEncontradasAgrupadasXml']['palavra'] )  
			
		
		if type( df['linksAgrupadosXml']['link'] ) == str:
			
			df['links'] = df['linksAgrupadosXml']['link']
			
		elif ( type( df['linksAgrupadosXml']['link'] ) == list ):
			
			df['links'] = ",".join( df['linksAgrupadosXml']['link'] )
			
		
		if type( df['trechosEncontradosAgrupadosXml']['trecho'] ) == str:
			
			df['trechos'] = df['trechosEncontradosAgrupadosXml']['trecho']
			
		elif ( type( df['trechosEncontradosAgrupadosXml']['trecho'] ) == list ):
			
			df['trechos'] = ",".join( df['trechosEncontradosAgrupadosXml']['trecho'] )
	
	except Exception as e:
		print('Deu ruim: ' + e)


def prepareDataSet( data ):
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