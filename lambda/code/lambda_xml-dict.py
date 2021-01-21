import urllib
import boto3
import xmltodict


def convert_xml_json( event, context ):
    
    s3 = boto3.client('s3')
    
    # get bucket name
    bucket = event['Records'][0]['s3']['bucket']['name']
    print("Bucket: " + bucket)
    
    #get the file/key name
    fineName = urllib.parse.unquote_plus( event['Records'][0]['s3']['object']['key'], encoding = 'utf-8' )
    print("File Name: " + fineName )
    
    try:
        
        # Fetch the file from s3
        response = s3.get_object( Bucket = bucket, Key = fineName )
        
        file = response['Body'].read()
        
        #return as dict
        doc = xmltodict.parse( file )
        print(doc)
        return doc
        
        
    except Exception as e:
        print( e )
        raise e
    