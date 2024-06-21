from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
)
import boto3


class Webinar1Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # crear instancia S3        
        bucket = s3.Bucket(self, id='MyBucket',
                           bucket_name= 'mybucketwebinar1',
                           )
        # crear directorios en instancia S3
        # Initialize a session using Amazon S3
        s3Instance = boto3.resource('s3')
        # Define the bucket name
        bucketName = "mybucketwebinar1"
        # Create the bucket object
        mybucket = s3Instance.Bucket(bucketName)
        # Create the folders (prefixes)
        folders = ['bronze/', 'silver/', 'gold/']
        for folder in folders:
            mybucket.put_object(Bucket=bucketName, Key=folder)
        # eliminar objetos de un S3        
        #s3Instance.Object(bucketName, 'gold').delete()



        # crear role IAM para acceso de lambda a S3
        iamRoleForLambdas = iam.Role(self, id= "IamRoleForLambdas",
                                     assumed_by= iam.ServicePrincipal(service="lambda.amazonaws.com"),
                                     role_name= "IamRoleForLambdas")
        iamRoleForLambdas.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        

        # crear función lambda test
        my_lambda = _lambda.Function(
            self, id= 'HelloHandler',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )

        # crear función lambda 1 (bronze a silver)
        lambdaBronzeASilver = _lambda.Function(
            self, id= 'bronzeASilver', function_name= "bronze_a_silver",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='bronze_a_silver.handler',
            role= iamRoleForLambdas
        )

        pandasLayer = _lambda.LayerVersion(self, id="pandasLayer",
                                           code= _lambda.Code.from_asset
                                           )


        # crear API gatewy con métodos correspondientes