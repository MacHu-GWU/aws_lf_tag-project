# -*- coding: utf-8 -*-

import enum
import json
from pathlib import Path
from typing import List, Dict, Union, Set, Type

import boto3
from box import Box

from . import boto_utils

DELIMITER = "____"


class Hashable:
    id: str

    def __eq__(self, other: 'Hashable') -> bool:
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Serializable:
    def serialize(self) -> dict:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, data) -> 'Serializable':
        raise NotImplementedError


# ------------------------------------------------------------------------------
# Principal
# ------------------------------------------------------------------------------
class Principal(Hashable, Serializable):
    def __init__(
        self,
        arn: str,
    ):
        self.arn = arn
        self.attachments: Dict[str, PrincipalAttachment] = dict()

    @property
    def attr_safe_name(self):
        return self.arn.split("/", 1)[1].replace("-", "_").replace(".", "_").replace("/", "__")

    @property
    def id(self) -> str:
        return self.arn

    def render_define(self) -> str:
        raise NotImplementedError

    # def attach(
    #     self,
    #     *tags: 'Tag',
    #     permissions: List[Type['Permission']] = None,
    # ):
    #     for tag in tags:
    #         self.bindings.setdefault(tag.id, dict())
    #         for permission in permissions:
    #             self.bindings[tag.id][permission.id] = dict(
    #                 tag=tag, permission=permission
    #             )
    #
    # def detach(
    #     self,
    #     *tags: 'Tag',
    # ):
    #     for tag in tags:
    #         tag_id = tag.id
    #         if tag_id in self.bindings:
    #             self.bindings.pop(tag_id)

    def serialize(self) -> dict:
        return dict(
            arn=self.arn,
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'Principal':
        return cls(arn=data["arn"])


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


class Resource(Hashable, Serializable):
    name: str
    tags: Dict[str, 'Tag']
    attachments: Dict[str, 'ResourceAttachment']

    @property
    def attr_safe_name(self) -> str:
        return to_attr_safe_name(self.name)

    @property
    def fullname(self) -> str:
        raise NotImplementedError

    @property
    def id(self) -> str:
        raise NotImplementedError

    @property
    def render_define(self) -> str:
        raise NotImplementedError

    @classmethod
    def deserialize(cls, data: dict) -> Union['Database', 'Table', 'Column']:
        if "account_id" in data:
            return Database.deserialize(data)
        elif "database" in data:
            return Table.deserialize(data)
        elif "table" in data:
            return Column.deserialize(data)
        else:
            raise Exception


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
        self.attachments: Dict[str, ResourceAttachment] = dict()

    def __repr__(self):
        return f'Database(account_id="{self.account_id}", region="{self.region}", name="{self.name}")'

    @property
    def attr_safe_region(self) -> str:
        return self.region.replace("-", "_")

    @property
    def fullname(self) -> str:
        return f'{self.account_id}{DELIMITER}{self.attr_safe_region}{DELIMITER}{self.attr_safe_name}'

    @property
    def id(self) -> str:
        return f'{self.account_id}{DELIMITER}{self.region}{DELIMITER}{self.name}'

    def render_define(self) -> str:
        return f'db_{self.fullname} = Database(account_id=account_id, region=region, name="{self.name}")'

    def serialize(self) -> dict:
        return dict(
            account_id=self.account_id,
            region=self.region,
            name=self.name,
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'Database':
        return cls(
            account_id=data["account_id"],
            region=data["region"],
            name=data["name"],
        )


class Table(Resource):
    def __init__(
        self,
        name: str,
        database: Database,
    ):
        self.name = name
        self.database = database

        assert isinstance(database, Database)

        self.c: Dict[str, Column] = Box()
        self.tags: Dict[str: Tag] = dict()
        self.attachments: Dict[str, ResourceAttachment] = dict()

    def __repr__(self):
        return f'Table(name="{self.name}", database={self.database.__repr__()})'

    @property
    def fullname(self) -> str:
        return f'{self.database.fullname}{DELIMITER}{self.attr_safe_name}'

    @property
    def id(self) -> str:
        return f'{self.database.id}{DELIMITER}{self.name}'

    def render_define(self) -> str:
        return f'tb_{self.fullname} = Table(name="{self.name}", database=db_{self.database.fullname})'

    def serialize(self) -> dict:
        return dict(
            name=self.name,
            database=self.database.serialize(),
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'Table':
        return cls(
            name=data["name"],
            database=Database.deserialize(data["database"]),
        )


class Column(Resource):
    def __init__(
        self,
        name: str,
        table: Table,
    ):
        self.name = name
        self.table = table

        assert isinstance(table, Table)

        self.tags: Dict[str: Tag] = dict()
        self.attachments: Dict[str, ResourceAttachment] = dict()

    def __repr__(self):
        return f'Column(name="{self.name}", table={self.table.__repr__()})'

    @property
    def fullname(self) -> str:
        return f'{self.table.fullname}{DELIMITER}{self.attr_safe_name}'

    @property
    def id(self) -> str:
        return f'{self.table.id}{DELIMITER}{self.name}'

    def render_define(self) -> str:
        return f'col_{self.fullname} = Column(name="{self.name}", table=tb_{self.table.fullname})'

    def serialize(self) -> dict:
        return dict(
            name=self.name,
            table=self.table.serialize(),
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'Column':
        return cls(
            name=data["name"],
            table=Table.deserialize(data["table"]),
        )


# ------------------------------------------------------------------------------
# Action
# ------------------------------------------------------------------------------
class Permission(Hashable, Serializable):
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
    def deserialize(cls, data: dict) -> 'Permission':
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

    @classmethod
    def _validate(cls):
        id_list = [permission.value.id for permission in cls]
        if len(id_list) != len(set(id_list)):
            raise ValueError


PermissionEnum._validate()


# ------------------------------------------------------------------------------
# LakeFormation Tag
# ------------------------------------------------------------------------------
class Tag(Hashable, Serializable):
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

        self.principal_attachments: Dict[str, PrincipalAttachment] = dict()
        self.resource_attachments: Dict[str, ResourceAttachment] = dict()

    @property
    def id(self):
        return f"{self.key}{DELIMITER}{self.value}"

    def serialize(self) -> dict:
        return dict(
            key=self.key,
            value=self.value,
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'Tag':
        tag = cls(
            key=data["key"],
            value=data["value"],
        )
        return tag

    def attach_to_principal(
        self,
        principal: Principal,
        permissions: List['Permission'],
    ):
        assert isinstance(principal, Principal)
        for permission in permissions:
            assert isinstance(permission, Permission)
            pa = PrincipalAttachment(
                tag=self,
                principal=principal,
                permission=permission,
            )
            self.principal_attachments[pa.id] = pa
            principal.attachments[pa.id] = pa

    def attach_to_resource(
        self,
        resource: Resource,
    ):
        assert isinstance(resource, Resource)
        ra = ResourceAttachment(
            tag=self,
            resource=resource,
        )
        self.resource_attachments[ra.id] = ra
        resource.attachments[ra.id] = ra


class PrincipalAttachment(Hashable, Serializable):
    def __init__(
        self,
        tag: Tag,
        principal: Principal,
        permission: Permission,
    ):
        self.tag = tag
        self.principal = principal
        self.permission = permission

    @property
    def id(self):
        return DELIMITER.join([
            self.tag.id, self.principal.id, self.permission.id,
        ])

    def serialize(self) -> dict:
        return dict(
            tag=self.tag.serialize(),
            principal=self.principal.serialize(),
            permission=self.permission.serialize(),
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'PrincipalAttachment':
        return cls(
            tag=Tag.deserialize(data["tag"]),
            principal=Principal.deserialize(data["principal"]),
            permission=Permission.deserialize(data["permission"]),
        )


class ResourceAttachment(Hashable, Serializable):
    def __init__(
        self,
        tag: Tag,
        resource: Resource,
    ):
        self.tag = tag
        self.resource = resource

    @property
    def id(self):
        return DELIMITER.join([
            self.tag.id, self.resource.id
        ])

    def serialize(self) -> dict:
        return dict(
            tag=self.tag.serialize(),
            resource=self.resource.serialize(),
        )

    @classmethod
    def deserialize(cls, data: dict) -> 'ResourceAttachment':
        return cls(
            tag=Tag.deserialize(data["tag"]),
            resource=Resource.deserialize(data["resource"]),
        )


# ------------------------------------------------------------------------------
# Playbook
# ------------------------------------------------------------------------------
class Playbook:
    def __init__(
        self,
        boto_ses: boto3.session.Session,
        workspace_dir: str,
    ):
        self.boto_ses: boto3.session.Session = boto_ses
        self.glue_client = boto_ses.client("glue")
        self.lf_client = boto_ses.client("lakeformation")
        self.sts_client = boto_ses.client("sts")
        self.region: str = self.boto_ses.region_name
        self.account_id: str = self.sts_client.get_caller_identity()["Account"]

        self.workspace_dir: Path = Path(workspace_dir)

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

    def apply_tags(self):
        # aggregate tags by key
        tags_mapper: Dict[str: Set[str]] = dict()
        for tag_id, tag in self.tags.items():
            try:
                tags_mapper[tag.key].add(tag.value)
            except KeyError:
                tags_mapper[tag.key] = {tag.value, }

        for tag_key, tag_values in tags_mapper.items():
            if boto_utils.is_tag_exists(self.lf_client, self.account_id, tag_key):
                raise NotImplementedError
            else:
                tag_values = list(tag_values)
                tag_values.sort()
                boto_utils.create_tag(
                    self.lf_client, self.account_id,
                    tag_key, tag_values
                )
            # if self.is_tag_exists(tag.key) is False:
            #     pass

    def apply(self):
        # self.apply_tags()
        p_deployed = Path(self.workspace_dir, "deployed.json")
        # pb = self.from
        p_deployed.write_text(json.dumps(self.serialize(), indent=4))
