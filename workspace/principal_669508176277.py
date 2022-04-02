# -*- coding: utf-8 -*-

from aws_lf_tag import IamUser, IamRole

role_lf_sme_demo_admin = IamRole(arn="arn:aws:iam::669508176277:role/lf-sme-demo-admin")

role_lf_sme_demo_limited = IamRole(arn="arn:aws:iam::669508176277:role/lf-sme-demo-limited")

role_lf_sme_demo_regular = IamRole(arn="arn:aws:iam::669508176277:role/lf-sme-demo-regular")