# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import (
    Principal, IamRole, IamUser, Permission, PermissionEnum
)

aws_profile = "my_aws_profile"
aws_region = "us-east-1"
aws_account_id = "111122223333"


class TestIamRole:
    def test(self):
        iam_role = IamRole(
            arn=f"arn:aws:iam::{aws_account_id}:role/ec2-role",
        )
        assert iam_role.attr_safe_name == "ec2_role"
        iam_role = IamRole(
            arn=f"arn:aws:iam::{aws_account_id}:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS"
        )
        assert iam_role.attr_safe_name == "aws_service_role__ecs_amazonaws_com__AWSServiceRoleForECS"

    def test_seder(self):
        iam_role = Principal(
            arn=f"arn:aws:iam::{aws_account_id}:role/ec2-role",
        )
        assert iam_role.serialize() == {"arn": "arn:aws:iam::111122223333:role/ec2-role"}
        iam_role1 = Principal.deserialize(iam_role.serialize())
        assert iam_role == iam_role1


class TestPermission:
    def test(self):
        assert PermissionEnum.Select.value.serialize() == {
            "id": "Select",
            "resource_type": "TABLE", "permission": "SELECT", "grantable": False
        }
        assert Permission.deserialize(
            PermissionEnum.Select.value.serialize()
        ).serialize() == PermissionEnum.Select.value.serialize()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
