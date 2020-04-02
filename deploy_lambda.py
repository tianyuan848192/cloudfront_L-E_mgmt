import boto3



def update_lambda(functionname, S3Bucket, S3Key, S3ObjectVersion):
    client_lambda = boto3.client('lambda')
    response_lambda = client_lambda.update_function_code(
        FunctionName=functionname,
        S3Bucket=S3Bucket,
        S3Key=S3Key,
        S3ObjectVersion=S3ObjectVersion,
        Publish=True
    )
    lambdaversion = response_lambda['FunctionArn']
    return lambdaversion


def lambda_handler(event, context):
    # Get S3 Object Meta
    S3Bucket = event['Records'][0]['s3']['bucket']['name']
    S3Key = event['Records'][0]['s3']['object']['key']
    S3ObjectVersion = event['Records'][0]['s3']['object']['versionId']
    # The S3 Object key must start up with lambda@edge name
    functionname = S3Key.split('.')[0]
    lambdaversion = update_lambda(functionname, S3Bucket, S3Key, S3ObjectVersion)
    client = boto3.client('cloudformation')
    response_cloudformation = client.update_stack(
        StackName='test',
        TemplateURL='https://cloudforamtion-bucket.s3.ap-northeast-2.amazonaws.com/cloudformation/cloudfront_lambda.yaml',
        Parameters=[
            {
                'ParameterKey': 'FirstLaunch',
                'ParameterValue': 'false'
            },
            {
                'ParameterKey': 'LambdaVersion',
                'ParameterValue': lambdaversion
            }
        ],
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
