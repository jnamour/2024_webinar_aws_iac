from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
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


        
        dev_vpc = ec2.Vpc.from_lookup(self, "dev_vpc", vpc_id="vpc-0e012da594c245474")
        security_group_id = 'sg-0dab238bf1283ed4d'
        security_group = ec2.SecurityGroup.from_security_group_id(self, 'MySecurityGroup', security_group_id)
        dev_subnet_selection = ec2.SubnetSelection(
            subnet_filters=[
                ec2.SubnetFilter.by_ids(
                    subnet_ids=["subnet-0ebec051f93e59c2d", "subnet-0dd7bdef565d054b7", "subnet-0c9bd662c4d537b53", "subnet-0e32d3adb3bf26d57", "subnet-0a3b49384eb3916b8", "subnet-0f6f169c7f496354f"]
                )
            ]
        )

        # crear función lambda gold a bd
        iamRoleForLambdaGoldADb = iam.Role(self, id= "iamRoleForLambdaGoldADb",
                                     assumed_by= iam.ServicePrincipal(service="lambda.amazonaws.com"),
                                     role_name= "iamRoleForLambdaGoldADb")
        iamRoleForLambdas.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"))
        iamRoleForLambdaGoldADb.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))        

        goldABd = _lambda.Function(
            self, id= 'goldABd', function_name= "gold_a_bd",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('lambda'),
            handler='gold_a_bd.lambda_handler',
            timeout= Duration.seconds(60),
            role= iamRoleForLambdaGoldADb,
            vpc= dev_vpc,
            security_groups=[security_group],
            vpc_subnets=dev_subnet_selection,
            allow_public_subnet=True
        )
        goldABd.add_layers(_lambda.LayerVersion.from_layer_version_arn(self, "pymongoLayer", "arn:aws:lambda:us-east-1:050826769311:layer:pymongo:4"))
        goldABd.add_layers(_lambda.LayerVersion.from_layer_version_arn(self, "pandasLayerGolABd", "arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python312:8"))


        # crear API gateway con métodos correspondientes

        '''
        api = apigateway.LambdaRestApi(
            self,
            "bronzeasilver",
            handler = lambdaBronzeASilver,
            proxy = False,
        )

        # Define the '/hello' resource with a GET method
        hello_resource = api.root.add_resource("bronzeasilver")
        hello_resource.add_method("POST")
        '''