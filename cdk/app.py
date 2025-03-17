#!/usr/bin/env python3
import os

import aws_cdk as cdk
from s3_upload import S3UploaderStack

app = cdk.App()
S3UploaderStack(app, "S3UploaderStack", description="Amazon S3 Serverless Upload",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    )

app.synth()