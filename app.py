#!/usr/bin/env python3

import aws_cdk as cdk

from webinar_1.webinar_1_stack import Webinar1Stack

env_EU = cdk.Environment(account="050826769311", region="us-east-1")

app = cdk.App()
Webinar1Stack(app, "Webinar1Stack", env=env_EU)

app.synth()
