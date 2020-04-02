工作原理
 
示例场景及代码
场景一： 首次部署CloudFront和Lambda@Edge

前置资源：
	创建S3 存储桶作为Lambda@Edge的代码artifacts。
	创建S3 存储桶，作为CloudFormation 存储模版的仓库，并将模版上传至存储桶
	执行CloudFormation的账号必须具备发布Lambda@Edge和更新CloudFront的权限








CloudFormation Template解释：

在CloudFormation模版中，定义了一个参数 FirstLaunch, 并在后面用Conditions 设置一个判断条件。
Parameters:
  FirstLaunch:
    Type: String
    Default: False
    AllowedValues:
      - True
      - False
    ConstraintDescription: True for Fist Launch the template, False for Update.
  LambdaVersion:
    Type: String
    Default: NONE
Conditions:
  FirstLaunch: !Equals [ !Ref FirstLaunch, True ]

在创建distribution的resource中，关联lambda@edge部分的时候会使用这个判断条件，如果FirstLaunch 为True的时候则这里的参数引用本模版中创建的LambdaVersion，如果为False，则引用从Template外传入的参数。
testdistribuationupdate:
    Type: 'AWS::CloudFront::Distribution'
    Properties:
      DistributionConfig:
        DefaultCacheBehavior:
          ViewerProtocolPolicy: allow-all
          ForwardedValues:
            QueryString: 'false'
          TargetOriginId: MyOrigin
          LambdaFunctionAssociations:
            - EventType: origin-request
              LambdaFunctionARN: !If [FirstLaunch, !Ref edgelambdaVersion, !Ref LambdaVersion]

创建资源
参考官方文档，创建堆栈
https://docs.aws.amazon.com/zh_cn/AWSCloudFormation/latest/UserGuide/cfn-using-console.html

注意：
1.	参数输入部分
如果首次执行FirstLaunch参数需要设置成false，LambdaVersion请选择默认值 NONE。


2.	权限部分：
执行CloudFormation的用户或者实体必须具备更新CloudFront 和Lambda@Edge的权限。
验证：
1.	验证堆栈
在CloudFormation创建完毕后，以下资源被创建
 
2.	登入CloudFront界面查看Distribution的Behavior
 
3.	访问CloudFront的页面，并与Lambda@Edge功能核对
 
场景二： 更新CloudFront上的Lambda@Edge
在此场景中，CloudFormation逻辑跟首次部署不同的地方在于参数的传入部分FirstLaunch 为false，并且需要输入LambdaVersion的部分。因此此部分的逻辑由deploy_lambda.py 来实现。

前置资源：
	完成CloudFormation的首次部署。
	创建一个Lambda，并从存储code的S3触发。





deploy_lambda.py代码解释：

update_lambda() 负责根据event中的捕获的信息，完成对应的Lambda@Edge的更新，并生成新的版本。并作为更新CloudFormation的输入参数进行后续操作

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
        TemplateURL='your template url',
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

注意：
	由于是deploy_lambda.py 程序执行lambda@edge的发布和更新cloudformation，并且更新CloudFront的distribution。因此执行实体要具备以上的权限。
	您上传的lambda@edge的zip包的名字需要跟lambda@edge函数的名字保持一致。
验证：
当您具备以上的前置条件和注意事项后





1.	上传代码到S3 的artifacts中,并查看版本信息
 
2.	检查CloudFormation是否处于更新状态，并等待更新完成（注意：因为更新CloudFront资源本身涉及到更新edge端的配置，因此可能耗时较长）
 
3.	检查CloudFront状态，直至状态变更为“已部署”
 
4.	检查Lambda@Edge效果（由于可能存在缓存，请清理缓存后验证）
 
Summary



