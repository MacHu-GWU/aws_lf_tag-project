# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import Playbook
from aws_lf_tag.tests import (
    ec2_iam_role,
    db, tb, col,
    tag_admin_y, tag_admin_n,
)


class TestPlaybook:
    pb: Playbook

    @classmethod
    def setup_class(cls):
        cls.pb = Playbook()
        cls.pb.add_tag(tag_admin_y)
        cls.pb.add_tag(tag_admin_n)




if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
