# -*- coding: utf-8 -*-

import pytest
from aws_lf_tag.core import (
    Resource, Database, Table, Column,
)

aws_profile = "my_aws_profile"
aws_region = "us-east-1"
aws_account_id = "111122223333"


class BaseTest:
    db = Database(
        account_id=aws_account_id,
        region=aws_region,
        name="db",
    )
    tb = Table(name="tb", database=db)
    col = Column(name="col", table=tb)


class TestResource(BaseTest):
    def test(self):
        assert self.db.fullname == "111122223333____us_east_1____db"
        assert self.db.id == "111122223333____us-east-1____db"
        assert self.db.attr_safe_name == "db"

        assert self.tb.fullname == "111122223333____us_east_1____db____tb"
        assert self.tb.id == "111122223333____us-east-1____db____tb"
        assert self.tb.attr_safe_name == "tb"

        assert self.col.fullname == "111122223333____us_east_1____db____tb____col"
        assert self.col.id == "111122223333____us-east-1____db____tb____col"
        assert self.col.attr_safe_name == "col"

    def test_seder(self):
        assert isinstance(Resource.deserialize(self.db.serialize()), Database)
        assert isinstance(Resource.deserialize(self.tb.serialize()), Table)
        assert isinstance(Resource.deserialize(self.col.serialize()), Column)


class TestDatabase(BaseTest):
    def test_seder(self):
        assert self.db.serialize() == {"account_id": "111122223333", "region": "us-east-1", "name": "db"}
        db = Database.deserialize(self.db.serialize())
        assert db == self.db


class TestTable(BaseTest):
    def test_seder(self):
        assert self.tb.serialize() == {
            "name": "tb",
            "database": {"account_id": "111122223333", "region": "us-east-1", "name": "db"}
        }
        tb = Table.deserialize(self.tb.serialize())
        assert tb == self.tb


class TestColumn(BaseTest):
    def test_seder(self):
        assert self.col.serialize() == {
            "name": "col",
            "table": {
                "name": "tb",
                "database": {
                    "account_id": "111122223333", "region": "us-east-1", "name": "db"
                }
            }
        }
        col = Column.deserialize(self.col.serialize())
        assert col == self.col


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
