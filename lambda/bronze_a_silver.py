import json
import boto3
import io
import pandas as pd

def lambda_handler(event, context):
    print("event: ", event)
    bucket_name = event["bucket"]
    text1 = event["text"]
    s3_path_1 = event["file_name"]
    bronzeFolder = event["bronzeFolder"]
    silverFolder = event["silverFolder"]

    s3_client = boto3.client("s3", "us-east-1")

    # leer archivos
    s3SourceFolder = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=bronzeFolder)
    for content in s3SourceFolder["Contents"]:
        if(content["Size"] != 0):
            print("File: ", content["Key"])
            obj = s3_client.get_object(Bucket=bucket_name, Key= content["Key"])
            df = pd.read_csv(obj['Body'])
            # Applying the condition
            df['a'] = df['a'].replace([0], 10)
            # escribir resultados
            with io.StringIO() as csv_buffer:
                df.to_csv(csv_buffer, index=False)
                destiny = silverFolder+"/"+content["Key"].split("/")[-1]
                print("destiny: ", destiny)
                response = s3_client.put_object(
                    Bucket=bucket_name, Key=destiny, Body=csv_buffer.getvalue()
                )

                status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

                if status == 200:
                    print(f"Successful S3 put_object response. Status - {status}")
                    print("df: ", df)
                else:
                    print(f"Unsuccessful S3 put_object response. Status - {status}")