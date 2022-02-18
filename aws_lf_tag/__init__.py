# -*- coding: utf-8 -*-

"""
Package Description.
"""

from ._version import __version__

__short_description__ = "AWS LakeFormation Tag based access management made easy"
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

from .core import (
    Principal,
    IamRole,
    IamUser,
    Resource,
    Database,
    Table,
    Column,
    PermissionEnum,
    Tag,
    Playbook,
)
from .gen_code import gen_resource, gen_principal

CreateTable = PermissionEnum.CreateTable.value
AlterDatabase = PermissionEnum.AlterDatabase.value
DropDatabase = PermissionEnum.DropDatabase.value
DescribeDatabase = PermissionEnum.DescribeDatabase.value
SuperDatabase = PermissionEnum.SuperDatabase.value
CreateTableGrantable = PermissionEnum.CreateTableGrantable.value
AlterDatabaseGrantable = PermissionEnum.AlterDatabaseGrantable.value
DropDatabaseGrantable = PermissionEnum.DropDatabaseGrantable.value
DescribeDatabaseGrantable = PermissionEnum.DescribeDatabaseGrantable.value
SuperDatabaseGrantable = PermissionEnum.SuperDatabaseGrantable.value
Select = PermissionEnum.Select.value
Insert = PermissionEnum.Insert.value
Delete = PermissionEnum.Delete.value
DescribeTable = PermissionEnum.DescribeTable.value
AlterTable = PermissionEnum.AlterTable.value
DropTable = PermissionEnum.DropTable.value
SuperTable = PermissionEnum.SuperTable.value
SelectGrantable = PermissionEnum.SelectGrantable.value
InsertGrantable = PermissionEnum.InsertGrantable.value
DeleteGrantable = PermissionEnum.DeleteGrantable.value
DescribeTableGrantable = PermissionEnum.DescribeTableGrantable.value
AlterTableGrantable = PermissionEnum.AlterTableGrantable.value
DropTableGrantable = PermissionEnum.DropTableGrantable.value
SuperTableGrantable = PermissionEnum.SuperTableGrantable.value
