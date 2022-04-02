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
    Permission,
    Tag,
    Playbook,
)
from .gen_code import gen_resource, gen_principal

CreateDatabase: Permission = PermissionEnum.CreateDatabase.value
AlterDatabase: Permission = PermissionEnum.AlterDatabase.value
DropDatabase: Permission = PermissionEnum.DropDatabase.value
DescribeDatabase: Permission = PermissionEnum.DescribeDatabase.value
SuperDatabase: Permission = PermissionEnum.SuperDatabase.value
CreateTable: Permission = PermissionEnum.CreateTable.value
CreateDatabaseGrantable: Permission = PermissionEnum.CreateDatabaseGrantable.value
AlterDatabaseGrantable: Permission = PermissionEnum.AlterDatabaseGrantable.value
DropDatabaseGrantable: Permission = PermissionEnum.DropDatabaseGrantable.value
DescribeDatabaseGrantable: Permission = PermissionEnum.DescribeDatabaseGrantable.value
SuperDatabaseGrantable: Permission = PermissionEnum.SuperDatabaseGrantable.value
CreateTableGrantable: Permission = PermissionEnum.CreateTableGrantable.value
Select: Permission = PermissionEnum.Select.value
Insert: Permission = PermissionEnum.Insert.value
Delete: Permission = PermissionEnum.Delete.value
DescribeTable: Permission = PermissionEnum.DescribeTable.value
AlterTable: Permission = PermissionEnum.AlterTable.value
DropTable: Permission = PermissionEnum.DropTable.value
SuperTable: Permission = PermissionEnum.SuperTable.value
SelectGrantable: Permission = PermissionEnum.SelectGrantable.value
InsertGrantable: Permission = PermissionEnum.InsertGrantable.value
DeleteGrantable: Permission = PermissionEnum.DeleteGrantable.value
DescribeTableGrantable: Permission = PermissionEnum.DescribeTableGrantable.value
AlterTableGrantable: Permission = PermissionEnum.AlterTableGrantable.value
DropTableGrantable: Permission = PermissionEnum.DropTableGrantable.value
SuperTableGrantable: Permission = PermissionEnum.SuperTableGrantable.value
