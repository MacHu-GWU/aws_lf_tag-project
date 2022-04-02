# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import (
    Tag, PrincipalAttachment, ResourceAttachment, PermissionEnum,
)
from aws_lf_tag.tests import (
    tag_admin_y, tag_admin_n, db, tb, col, ec2_iam_role,
)


class TestPrincipalAttachment:
    def test(self):
        pa = PrincipalAttachment(tag=tag_admin_y, principal=ec2_iam_role, permission=PermissionEnum.DescribeTable.value)
        assert pa.serialize() == {
            "tag": {"key": "Admin", "value": "y"},
            "principal": {"arn": "arn:aws:iam::111122223333:role/ec2-role"},
            "permission": {
                "id": "DescribeTable",
                "resource_type": "TABLE",
                "permission": "DESCRIBE",
                "grantable": False
            },
        }

        pa1 = PrincipalAttachment.deserialize(pa.serialize())
        assert pa1 == pa


class TestResourceAttachment:
    def test(self):
        ra = ResourceAttachment(tag=tag_admin_y, resource=db)
        assert ra.serialize() == {
            "tag": {"key": "Admin", "value": "y"},
            "resource": {"account_id": "111122223333", "region": "us-east-1", "name": "db"},
        }

        ra1 = ResourceAttachment.deserialize(ra.serialize())
        assert ra1 == ra


class TestTag:
    def test(self):
        tag1 = Tag(key="Admin", value="y")
        tag2 = Tag(key="Admin", value="n")
        tag3 = Tag(key="Regular", value="y")
        tag4 = Tag(key="Regular", value="n")
        assert tag1.id == "Admin____y"
        tag_set = {tag1, tag2, tag3, tag4}
        assert tag1 in tag_set

    def test_serde(self):
        tag = Tag(key="Admin", value="y")
        assert tag.serialize() == {
            "key": "Admin",
            "value": "y",
        }
        tag1 = Tag.deserialize(tag.serialize())
        assert tag1 == tag

        tag2 = Tag.deserialize(
            dict(
                key="Admin", value="y",
                principal_attachments=[1, 2, 3],
                resource_attachments=[1, 2, 3],
            )
        )
        assert tag2 == tag

    def test_attach_to(self):
        assert len(tag_admin_y.principal_attachments) == 0
        tag_admin_y.attach_to_principal(ec2_iam_role, [PermissionEnum.DescribeTable.value])
        # assert len(tag_admin_y.principal_attachments) == 1
        # assert len(ec2_iam_role.attachments) == 1


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
