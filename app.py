#!/usr/bin/env python3

import aws_cdk as cdk

from webinar_1.webinar_1_stack import Webinar1Stack


app = cdk.App()
Webinar1Stack(app, "Webinar1Stack")

app.synth()
