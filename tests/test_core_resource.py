# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import (
    Database, Table, Column,
)

aws_profile = "my_aws_profile"
aws_region = "us-east-1"
aws_account_id = "111122223333"


class TestResource:
    def test(self):
        db = Database(
            account_id=aws_account_id,
            region=aws_region,
            name="db",
        )
        assert db.fullname == "111122223333__us_east_1__db"
        assert db.id == "111122223333__us-east-1__db"

        tb = Table(name="tb", database=db)
        assert tb.fullname == "111122223333__us_east_1__db__tb"
        assert tb.id == "111122223333__us-east-1__db__tb"

        col = Column(name="col", table=tb)
        assert col.fullname == "111122223333__us_east_1__db__tb__col"
        assert col.id == "111122223333__us-east-1__db__tb__col"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
