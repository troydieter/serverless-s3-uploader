from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigw,
    Stack, Duration, CfnOutput, Tags
)


class S3UploaderStack(Stack):
    def __init__(self, scope, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        Tags.of(self).add("project", "serverless-s3-uploader")
        Tags.of(self).add(
            "repo", "https://github.com/troydieter/serverless-s3-uploader")

        # Create S3 Bucket
        s3_bucket = s3.Bucket(
            self, "S3UploaderBucket",
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET,
                        s3.HttpMethods.PUT,
                        s3.HttpMethods.POST,
                        s3.HttpMethods.DELETE,
                        s3.HttpMethods.HEAD
                    ],
                    allowed_origins=["*"],  # Allow all origins
                    allowed_headers=["*"],  # Allow all headers
                    # Optional, useful for frontend handling
                    exposed_headers=["ETag"]
                )
            ]
        )

        # Create IAM Role for Lambda
        lambda_role = iam.Role(
            self, "S3UploaderLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject",
                         "s3:DeleteObject", "s3:ListBucket"],
                resources=[s3_bucket.bucket_arn, f"{s3_bucket.bucket_arn}/*"]
            )
        )

        # Add Inline Policy for S3 Access
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:PutObject", "s3:GetObject",
                         "s3:DeleteObject", "s3:ListBucket"],
                resources=[s3_bucket.bucket_arn, f"{s3_bucket.bucket_arn}/*"]
            )
        )

        # Create Lambda Function
        uploader_lambda = _lambda.Function(
            self, "S3UploaderFunction",
            runtime=_lambda.Runtime.NODEJS_18_X,
            handler="app.handler",
            # Ensure this path contains your Lambda code
            code=_lambda.Code.from_asset("s3UploaderFunction"),
            memory_size=256,
            timeout=Duration.seconds(10),
            environment={
                "UploadBucket": s3_bucket.bucket_name
            },
            role=lambda_role
        )

        # API Gateway Integration with Throttling
        api = apigw.RestApi(self, "S3UploaderApi",
                            deploy_options=apigw.StageOptions(
                                stage_name="prod",
                                throttling_burst_limit=100,
                                throttling_rate_limit=500
                            )
                            )

        # Add an API Key
        api_key = api.add_api_key("S3UploaderApiKey")

        # Create a Usage Plan for the API Key
        usage_plan = api.add_usage_plan(
            "S3UploaderUsagePlan",
            name="S3UploaderUsagePlan",
            api_stages=[apigw.UsagePlanPerApiStage(
                api=api, stage=api.deployment_stage)],
            throttle=apigw.ThrottleSettings(rate_limit=100, burst_limit=50)
        )
        usage_plan.add_api_key(api_key)

        s3_uploader_resource = api.root.add_resource("upload")
        s3_uploader_resource.add_method(
            "GET",
            apigw.LambdaIntegration(uploader_lambda),
            api_key_required=True
        )

        # Outputs
        CfnOutput(self, "S3UploaderFunctionArn",
                  value=uploader_lambda.function_arn)
        CfnOutput(self, "S3UploaderLambdaRoleArn", value=lambda_role.role_arn)
        CfnOutput(self, "S3BucketName", value=s3_bucket.bucket_name)
        CfnOutput(self, "S3UploaderApiKey", value=api_key.key_id)
