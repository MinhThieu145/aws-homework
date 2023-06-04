#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_ec2_app.cdk_ec2_app_stack import CdkEc2AppStack


app = cdk.App()
CdkEc2AppStack(app, "cdk-ec2-app")

app.synth()
