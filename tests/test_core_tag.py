# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import Tag


class TestTag:
    def test(self):
        tag1 = Tag(key="Admin", value="y")
        tag2 = Tag(key="Admin", value="n")
        tag3 = Tag(key="Regular", value="y")
        tag4 = Tag(key="Regular", value="n")
        assert tag1.id == "Admin____y"
        tag_set = {tag1, tag2, tag3, tag4}
        assert tag1 in tag_set


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
