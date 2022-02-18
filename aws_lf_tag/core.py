# -*- coding: utf-8 -*-

import enum
from typing import List, Dict, Union, Type
from box import Box

DELIMITER = "____"


# ------------------------------------------------------------------------------
# Principal
# ------------------------------------------------------------------------------
class Principal:
    def __init__(
        self,
        arn: str,
    ):
        self.arn = arn
        self.bindings: Dict[str: Dict[str: Dict[str, Union[Tag, Permission]]]] = dict()

    @property
    def attr_safe_name(self):
        return self.arn.split("/", 1)[1].replace("-", "_").replace(".", "_").replace("/", "__")

    @property
    def id(self):
        return self.arn

    def render_define(self) -> str:
        raise NotImplementedError

    def attach(
        self,
        *tags: 'Tag',
        permissions: List[Type['Permission']] = None,
    ):
        for tag in tags:
            self.bindings.setdefault(tag.id, dict())
            for permission in permissions:
                self.bindings[tag.id][permission.id] = dict(
                    tag=tag, permission=permission
                )

    def detach(
        self,
        *tags: 'Tag',
    ):
        for tag in tags:
            tag_id = tag.id
            if tag_id in self.bindings:
                self.bindings.pop(tag_id)


class IamUser(Principal):
    def render_define(self) -> str:
        return f'user_{self.attr_safe_name} = IamUser(arn="{self.arn}")'


class IamRole(Principal):
    def render_define(self) -> str:
        return f'role_{self.attr_safe_name} = IamRole(arn="{self.arn}")'


# ------------------------------------------------------------------------------
# Resource
# ------------------------------------------------------------------------------
def to_attr_safe_name(name):
    return name.replace("-", "_").replace(".", "_dot_")


class Resource:
    name: str
    tags: Dict[str, 'Tag']

    @property
    def attr_safe_name(self):
        return to_attr_safe_name(self.name)

    @property
    def fullname(self):
        raise NotImplementedError

    @property
    def id(self):
        raise NotImplementedError

    @property
    def render_define(self):
        raise NotImplementedError

    def attach(
        self,
        *tags: 'Tag',
    ):
        for tag in tags:
            self.tags.setdefault(tag.id, tag)

    def detach(
        self,
        *tags: 'Tag',
    ):
        for tag in tags:
            tag_id = tag.id
            if tag_id in self.tags:
                self.tags.pop(tag_id)

    def serialize(self) -> dict:
        raise NotImplementedError


class Database(Resource):
    def __init__(
        self,
        account_id: str,
        region: str,
        name: str,
    ):
        self.account_id = account_id
        self.region = region
        self.name = name
        self.t: Dict[str, Table] = Box()
        self.tags: Dict[str: Tag] = dict()

    def __repr__(self):
        return f'Database(account_id="{self.account_id}", region="{self.region}", name="{self.name}")'

    @property
    def attr_safe_region(self):
        return self.region.replace("-", "_")

    @property
    def fullname(self):
        return f'{self.account_id}__{self.attr_safe_region}__{self.attr_safe_name}'

    @property
    def id(self):
        return f'{self.account_id}__{self.region}__{self.name}'

    def render_define(self) -> str:
        return f'db_{self.fullname} = Database(account_id=account_id, region=region, name="{self.name}")'

    def serialize(self) -> dict:
        return dict(
            account_id=self.account_id,
            region=self.region,
            name=self.name,
            tags={
                tag_id: tag.serialize()
                for tag_id, tag in self.tags.items()
            }
        )


class Table(Resource):
    def __init__(
        self,
        name: str,
        database: Database,
    ):
        self.name = name
        self.database = database
        self.c: Dict[str, Column] = Box()
        self.tags: Dict[str: Tag] = dict()

    def __repr__(self):
        return f'Table(name="{self.name}", database={self.database.__repr__()})'

    @property
    def fullname(self):
        return f'{self.database.fullname}__{self.attr_safe_name}'

    @property
    def id(self):
        return f'{self.database.id}__{self.name}'

    def render_define(self) -> str:
        return f'tb_{self.fullname} = Table(name="{self.name}", database=db_{self.database.fullname})'

    def serialize(self) -> dict:
        return dict(
            name=self.name,
            database=self.database.serialize(),
            tags={
                tag_id: tag.serialize()
                for tag_id, tag in self.tags.items()
            }
        )


class Column(Resource):
    def __init__(
        self,
        name: str,
        table: Table,
    ):
        self.name = name
        self.table = table
        self.tags: Dict[str: Tag] = dict()

    def __repr__(self):
        return f'Column(name="{self.name}", table={self.table.__repr__()})'

    @property
    def fullname(self):
        return f'{self.table.fullname}__{self.attr_safe_name}'

    @property
    def id(self):
        return f'{self.table.id}__{self.name}'

    def render_define(self) -> str:
        return f'col_{self.fullname} = Column(name="{self.name}", table=tb_{self.table.fullname})'

    def serialize(self) -> dict:
        return dict(
            name=self.name,
            table=self.table.serialize(),
            tags={
                tag_id: tag.serialize()
                for tag_id, tag in self.tags.items()
            }
        )


# ------------------------------------------------------------------------------
# Action
# ------------------------------------------------------------------------------
class Permission:
    """

    """

    def __init__(
        self,
        id: str,
        resource_type: str,
        permission: str,
        grantable: bool,
    ):
        self.id = id
        self.resource_type = resource_type
        self.permission = permission
        self.grantable = grantable

    def serialize(self) -> dict:
        return dict(
            id=self.id,
            resource_type=self.resource_type,
            permission=self.permission,
            grantable=self.grantable,
        )

    @classmethod
    def deserialize(cls, data: dict):
        return PermissionEnum[data["id"]].value


class PermissionEnum(enum.Enum):
    CreateTable = Permission(
        id="CreateTable",
        resource_type="DATABASE",
        permission="CREATE_DATABASE",
        grantable=False,
    )

    AlterDatabase = Permission(
        id="AlterDatabase",
        resource_type="DATABASE",
        permission="ALTER",
        grantable=False,
    )

    DropDatabase = Permission(
        id="DropDatabase",
        resource_type="DATABASE",
        permission="DROP",
        grantable=False,
    )

    DescribeDatabase = Permission(
        id="DescribeDatabase",
        resource_type="DATABASE",
        permission="DESCRIBE",
        grantable=False,
    )

    SuperDatabase = Permission(
        id="SuperDatabase",
        resource_type="DATABASE",
        permission="ALL",
        grantable=False,
    )

    CreateTableGrantable = Permission(
        id="CreateTableGrantable",
        resource_type="DATABASE",
        permission="CREATE_DATABASE",
        grantable=True,
    )

    AlterDatabaseGrantable = Permission(
        id="AlterDatabaseGrantable",
        resource_type="DATABASE",
        permission="ALTER",
        grantable=True,
    )

    DropDatabaseGrantable = Permission(
        id="DropDatabaseGrantable",
        resource_type="DATABASE",
        permission="DROP",
        grantable=True,
    )

    DescribeDatabaseGrantable = Permission(
        id="DescribeDatabaseGrantable",
        resource_type="DATABASE",
        permission="DESCRIBE",
        grantable=True,
    )

    SuperDatabaseGrantable = Permission(
        id="SuperDatabaseGrantable",
        resource_type="DATABASE",
        permission="ALL",
        grantable=True,
    )

    Select = Permission(
        id="Select",
        resource_type="TABLE",
        permission="SELECT",
        grantable=False,
    )

    Insert = Permission(
        id="Insert",
        resource_type="TABLE",
        permission="INSERT",
        grantable=False,
    )

    Delete = Permission(
        id="Delete",
        resource_type="TABLE",
        permission="DELETE",
        grantable=False,
    )

    DescribeTable = Permission(
        id="DescribeTable",
        resource_type="TABLE",
        permission="DESCRIBE",
        grantable=False,
    )

    AlterTable = Permission(
        id="AlterTable",
        resource_type="TABLE",
        permission="ALTER",
        grantable=False,
    )

    DropTable = Permission(
        id="DropTable",
        resource_type="TABLE",
        permission="DROP",
        grantable=False,
    )

    SuperTable = Permission(
        id="SuperTable",
        resource_type="TABLE",
        permission="ALL",
        grantable=False,
    )

    SelectGrantable = Permission(
        id="SelectGrantable",
        resource_type="TABLE",
        permission="SELECT",
        grantable=True,
    )

    InsertGrantable = Permission(
        id="InsertGrantable",
        resource_type="TABLE",
        permission="INSERT",
        grantable=True,
    )

    DeleteGrantable = Permission(
        id="DeleteGrantable",
        resource_type="TABLE",
        permission="DELETE",
        grantable=True,
    )

    DescribeTableGrantable = Permission(
        id="DescribeTableGrantable",
        resource_type="TABLE",
        permission="DESCRIBE",
        grantable=True,
    )

    AlterTableGrantable = Permission(
        id="AlterTableGrantable",
        resource_type="TABLE",
        permission="ALTER",
        grantable=True,
    )

    DropTableGrantable = Permission(
        id="DropTableGrantable",
        resource_type="TABLE",
        permission="DROP",
        grantable=True,
    )

    SuperTableGrantable = Permission(
        id="SuperTableGrantable",
        resource_type="TABLE",
        permission="ALL",
        grantable=True,
    )


# ------------------------------------------------------------------------------
# LakeFormation Tag
# ------------------------------------------------------------------------------
class Tag:
    def __init__(
        self,
        key: str,
        value: str,
        pb: 'Playbook' = None,
    ):
        self.key = key
        self.value = value
        if pb is not None:  # pragma: no cover
            pb.add_tag(self)

        self.resources: Dict[str, Resource]

    @property
    def id(self):
        return f"{self.key}____{self.value}"

    def __hash__(self):
        return hash(self.id)

    def serialize(self) -> dict:
        return dict(key=self.key, value=self.value)

    @classmethod
    def deserialize(cls, data: dict):
        return Tag(key=data["key"], value=data["value"])


class Binding:
    def __init__(
        self,
        tag: Tag = None,
        principal: Principal = None,
        resource: Resource = None,
        permission: Permission = None,
    ):
        self.tag = tag
        self.principal = principal
        self.resource = resource
        self.permission = permission

    @property
    def id(self):
        return DELIMITER.join([
            str(None) if (self.tag is None) else self.tag.id,
            str(None) if (self.principal is None) else self.principal.id,
            str(None) if (self.resource is None) else self.resource.id,
            str(None) if (self.permission is None) else self.permission.id,
        ])


# ------------------------------------------------------------------------------
# Playbook
# ------------------------------------------------------------------------------
class Playbook:
    def __init__(self, boto_ses):
        self.boto_ses = boto_ses
        self.principals: Dict[str, Principal] = dict()
        self.resources: Dict[str, Resource] = dict()
        self.tags: Dict[str, Tag] = dict()

    def add_principal(self, principal: Principal):
        self.principals[principal.id] = principal

    def add_resource(self, resource: Resource):
        self.resources[resource.id] = resource

    def add_tag(self, tag: Tag):
        self.tags[tag.id] = tag

    def serialize(self) -> dict:
        data: Dict[
            str,
            Dict[
                str,
                Dict[
                    str,
                    Union[Tag, Principal, Resource]
                ]
            ]
        ] = {
            "tags": {}, "principals": {}, "resources": {},
        }

        for tag_id, tag in self.tags.items():
            data["tags"][tag_id] = tag.serialize()

        for resource_id, resource in self.resources.items():
            data["resources"][resource_id] = resource.serialize()

        return data

    def apply(self):
        pass
