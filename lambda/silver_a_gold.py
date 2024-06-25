import json
import boto3
import io
import pandas as pd

def lambda_handler(event, context):
    bucket_name = event["bucket"]
    silverFolder = event["silverFolder"]
    goldFolder = event["goldFolder"]

    s3_client = boto3.client("s3", "us-east-1")

    # leer archivos
    s3SourceFolder = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=silverFolder)
    dfs = []
    
    for content in s3SourceFolder["Contents"]:
        # si es archivo
        if(content["Size"] != 0):
            print("File: ", content["Key"])
            obj = s3_client.get_object(Bucket=bucket_name, Key= content["Key"])
            df = pd.read_csv(obj['Body'])
            dfs.append(df)

    with io.StringIO() as csv_buffer:
        dfConcatenar = pd.concat(dfs)
        dfConcatenar.to_csv(csv_buffer, index=False)
        destiny = goldFolder+"/"+"archivos_concatenados.csv"
        print("destiny: ", destiny)
        response = s3_client.put_object(
            Bucket=bucket_name, Key=destiny, Body=csv_buffer.getvalue()
        )

        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

        if status == 200:
            print(f"Successful S3 put_object response. Status - {status}")
            print("df: ", dfConcatenar)
        else:
            print(f"Unsuccessful S3 put_object response. Status - {status}")