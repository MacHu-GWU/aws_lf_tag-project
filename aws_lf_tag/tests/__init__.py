# -*- coding: utf-8 -*-

from ..core import (
    IamRole, IamUser,
    Database, Table, Column,
    Tag, PrincipalAttachment, ResourceAttachment
)

aws_profile = "my_aws_profile"
aws_region = "us-east-1"
aws_account_id = "111122223333"

# Principal
ec2_iam_role = IamRole(
    arn=f"arn:aws:iam::{aws_account_id}:role/ec2-role",
)
ecs_service_role = IamRole(
    arn=f"arn:aws:iam::{aws_account_id}:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS"
)
alice_iam_user = IamUser(
    arn=f"arn:aws:iam::{aws_account_id}:user/alice"
)

# Resource
db = Database(
    account_id=aws_account_id,
    region=aws_region,
    name="db",
)
tb = Table(name="tb", database=db)
col = Column(name="col", table=tb)

# Tag
tag_admin_y = Tag(key="Admin", value="y")
tag_admin_n = Tag(key="Admin", value="n")
tag_regular_y = Tag(key="Regular", value="y")
tag_regular_n = Tag(key="Regular", value="n")
