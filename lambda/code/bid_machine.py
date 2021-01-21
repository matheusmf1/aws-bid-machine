import xmltodict
import json

import boto3


def getAllBuckets():

	s3 = boto3.resource('s3')
 
	for bucket in s3.buckets.all():
		print(bucket.name)


def xmlToDict( file ):
	doc = xmltodict.parse( file )

	print('---------------------Dict---------------------')
	print( doc )
	return doc


def xmlToJson( file ):
	doc = xmltodict.parse( file )

	jsonXml = json.dumps( doc )
	print('---------------------Json---------------------')
	print( jsonXml )
	return jsonXml



def getAllFiles():
	s3 = boto3.resource('s3')
	bucket = s3.Bucket( 'rhs-xml-test' )

	for content in bucket.objects.all():
		print(content.key)


def getRhsBucketContent():

	s3_client = boto3.client('s3')
	s3_resource = boto3.resource('s3')

	bucket = s3_resource.Bucket( 'rhs-xml-test' )

	for content in bucket.objects.all():
		
		data = s3_client.get_object( Bucket = 'rhs-xml-test', Key = content.key )
		contents = data['Body'].read()

		xmlToDict( contents )
	

getRhsBucketContent()