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
        s3Instance = boto3.resource('s3')
        # crear bucket
        bucketName = "mybucketwebinar1"
        mybucket = s3Instance.Bucket(bucketName)
        # crear carpetas
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

        # crear función lambda bronze a silver
        lambdaBronzeASilver = _lambda.Function(
            self, id= 'bronzeASilver', function_name= "bronze_a_silver",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='bronze_a_silver.lambda_handler',
            timeout= Duration.seconds(20),
            role= iamRoleForLambdas
        )

        # crear función lambda silver a gold
        # crear función lambda 1 (bronze a silver)
        lambdaSilverAGold = _lambda.Function(
            self, id= 'silverAGold', function_name= "silver_a_gold",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='silver_a_gold.lambda_handler',
            timeout= Duration.seconds(20),
            role= iamRoleForLambdas
        )
        
        # agregar layer con arn
        lambdaSilverAGold.add_layers(_lambda.LayerVersion.from_layer_version_arn(self, "pandasLayer", "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:8"))

        # crear API gateway con métodos correspondientes