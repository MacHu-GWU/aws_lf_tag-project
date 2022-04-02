# -*- coding: utf-8 -*-

import enum
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Union, Set, Tuple, Iterable, Type, Any

import boto3
from box import Box
from colorama import Fore, Back, Style

from . import boto_utils
from .logger import logger

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

    def __repr__(self):
        return f'{self.__class__.__name__}(arn="{self.arn}")'

    @property
    def attr_safe_name(self):
        return self.arn.split("/", 1)[1].replace("-", "_").replace(".", "_").replace("/", "__")

    @property
    def id(self) -> str:
        return self.arn

    def render_define(self) -> str:
        raise NotImplementedError

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
    get_add_remove_lf_tags_arg_name: str

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

    @property
    def get_add_remove_lf_tags_arg_value(self) -> dict:
        raise NotImplementedError


class Database(Resource):
    get_add_remove_lf_tags_arg_name = "Database"

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

    @property
    def get_add_remove_lf_tags_arg_value(self) -> dict:
        return dict(
            CatalogId=self.account_id,
            Name=self.name,
        )


class Table(Resource):
    get_add_remove_lf_tags_arg_name = "Table"

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
        return f'Table(database={self.database!r}, name="{self.name}")'

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

    @property
    def get_add_remove_lf_tags_arg_value(self) -> dict:
        return dict(
            CatalogId=self.database.account_id,
            DatabaseName=self.database.name,
            Name=self.name,
        )


class Column(Resource):
    get_add_remove_lf_tags_arg_name = "TableWithColumns"

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
        return f'Column(table={self.table!r}, name="{self.name}")'

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

    @property
    def get_add_remove_lf_tags_arg_value(self) -> dict:
        return dict(
            CatalogId=self.table.database.account_id,
            DatabaseName=self.table.database.name,
            Name=self.table.name,
            ColumnNames=[self.name, ]
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

    def __repr__(self):
        return f'{self.__class__.__name__}(id="{self.id}", resource_type="{self.resource_type}", permission="{self.permission}", grantable={self.grantable})'

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
    """

    """
    CreateDatabase = Permission(
        id="CreateDatabase",
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

    CreateTable = Permission(
        id="CreateTable",
        resource_type="DATABASE",
        permission="CREATE_TABLE",
        grantable=False,
    )

    CreateDatabaseGrantable = Permission(
        id="CreateDatabaseGrantable",
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

    CreateTableGrantable = Permission(
        id="CreateTableGrantable",
        resource_type="DATABASE",
        permission="CREATE_TABLE",
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

    def __repr__(self):
        return f'{self.__class__.__name__}(key="{self.key}", value="{self.value}")'

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
        principal: 'Principal',
        permissions: List['Permission'],
    ):
        """
        Ref:

        - Grant: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.batch_grant_permissions
        - Revoke: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.batch_revoke_permissions

        :param principal:
        :param permissions:
        :return:
        """
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
def get_local_and_utc_now() -> Tuple[datetime, datetime]:
    """
    Get current time in both local timezone format and utc format.
    """
    local_now = datetime.now().replace(microsecond=0)
    local_tz = local_now.astimezone().tzinfo
    local_now = local_now.replace(tzinfo=local_tz)
    utc_now = local_now.astimezone(timezone.utc)
    return (local_now, utc_now)


def get_diff_and_inter(
    dct1: Dict[str, Any],
    dct2: Dict[str, Any],
) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Each deployed ``Object`` usually has a unique id. ``Mapper`` is a dictionary
    data structure that stores a collection of ``Object``. Key is the
    ``Object`` id, value is the ``Object`` instance.

    Given a new ``Mapper`` and a deployed ``Mapper``, it is very common to
    find out which ``Object`` should be added, should be delayed and should be
    updated.

    This utility function takes two parameter

    1. new object ``Mapper``
    2. deployed object ``Mapper``

    Returns three set data structure

    1. to add object id set
    2. to delete object id set
    3. to update object id set

    :param dct1:
    :param dct2:
    :return:
    """
    s1 = set(dct1)
    s2 = set(dct2)
    return (s1.difference(s2), s2.difference(s1), s1.intersection(s2))


def grouper_list(l: Iterable, n: int) -> List[list]:
    """
    Evenly divide list into fixed-length piece, no filled value if chunk
    size smaller than fixed-length.

    Example::

        >>> list(grouper_list(range(10), n=3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    chunk = list()
    counter = 0
    for item in l:
        counter += 1
        chunk.append(item)
        if counter == n:
            yield chunk
            chunk = list()
            counter = 0
    if len(chunk) > 0:
        yield chunk

class Playbook:
    def __init__(
        self,
        boto_ses: boto3.session.Session = None,
        workspace_dir: str = None,
        _skip_validation: bool = False
    ):
        if not _skip_validation:
            assert isinstance(boto_ses, boto3.session.Session)
            workspace_dir = Path(workspace_dir)
            assert workspace_dir.exists()

        self.boto_ses: boto3.session.Session = boto_ses

        if not _skip_validation:
            self.glue_client = boto_ses.client("glue")
            self.lf_client = boto_ses.client("lakeformation")
            self.sts_client = boto_ses.client("sts")
            self.region: str = self.boto_ses.region_name
            self.account_id: str = self.sts_client.get_caller_identity()["Account"]

            self.workspace_dir: Path = Path(workspace_dir)
            self.p_deployed: Path = Path(self.workspace_dir, f"deployed-{self.account_id}-{self.region}.json")

        self.deployed_pb: Union[Playbook, None] = None

        self.tags: Dict[str, Tag] = dict()

    def add_tag(self, tag: Tag):
        self.tags[tag.id] = tag

    def serialize(self) -> dict:
        local_now, utc_now = get_local_and_utc_now()
        try:
            username = Path.home().name
        except:
            username = "unknown"
        data: Dict[
            str, Dict[
                str, Dict[
                    str, Union[Tag, Principal, Resource]
                ]
            ]
        ] = {
            "deployed_by": username,
            "deployed_at_local_time": local_now.isoformat(),
            "deployed_at_utc_time": utc_now.isoformat(),
            "tags": {},
        }

        for tag_id, tag in self.tags.items():
            tag_dct = tag.serialize()
            tag_dct["principal_attachments"] = {
                pa_id: pa.serialize()
                for pa_id, pa in tag.principal_attachments.items()
            }
            tag_dct["resource_attachments"] = {
                ra_id: ra.serialize()
                for ra_id, ra in tag.resource_attachments.items()
            }
            data["tags"][tag.id] = tag_dct

        return data

    @classmethod
    def deserialize(cls, data: dict) -> 'Playbook':
        pb = cls(_skip_validation=True)
        for tag_id, tag_dct in data.get("tags", dict()).items():
            tag = Tag.deserialize(tag_dct)
            for pa_id, pa_dct in tag_dct.get("principal_attachments", dict()).items():
                tag.principal_attachments[pa_id] = PrincipalAttachment.deserialize(pa_dct)
            for ra_id, ra_dct in tag_dct.get("resource_attachments", dict()).items():
                tag.resource_attachments[ra_id] = ResourceAttachment.deserialize(ra_dct)
            pb.tags[tag_id] = tag
        return pb

    @property
    def tag_mapper(self) -> Dict[str, Set[str]]:
        """
        Aggregate tag by key, and put values for the same key into a set.
        """
        mapper = dict()
        for tag_id, tag in self.tags.items():
            try:
                mapper[tag.key].add(tag.value)
            except KeyError:
                mapper[tag.key] = {tag.value, }
        return mapper

    @property
    def principal_attachment_mapper(self) -> Dict[str, PrincipalAttachment]:
        mapper = dict()
        for tag_id, tag in self.tags.items():
            for pa_id, pa in tag.principal_attachments.items():
                mapper[pa_id] = pa
        return mapper

    @property
    def resource_attachment_mapper(self) -> Dict[str, ResourceAttachment]:
        mapper = dict()
        for tag_id, tag in self.tags.items():
            for ra_id, ra in tag.resource_attachments.items():
                mapper[ra_id] = ra
        return mapper

    def apply_tags(
        self,
        verbose=True,
        dry_run=False,
    ):
        """
        Ref:

        - Create: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.create_lf_tag
        - Update: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.update_lf_tag
        - Delete: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.delete_lf_tag
        """
        if not verbose:
            logger.enable_verbose = False

        new_tag_mapper = self.tag_mapper
        deployed_tag_mapper = self.deployed_pb.tag_mapper

        (
            to_create_tag_id_set,
            to_delete_tag_id_set,
            to_update_tag_id_set,
        ) = get_diff_and_inter(new_tag_mapper, deployed_tag_mapper)

        to_create_tag_kwargs = [
            dict(
                CatalogId=self.account_id,
                TagKey=tag_key,
                TagValues=list(new_tag_mapper[tag_key]),
            )
            for tag_key in to_create_tag_id_set
        ]

        to_delete_tag_kwargs = [
            dict(
                CatalogId=self.account_id,
                TagKey=tag_key,
            )
            for tag_key in to_delete_tag_id_set
        ]

        to_update_tag_kwargs = list()
        for tag_key in to_update_tag_id_set:
            new_values = new_tag_mapper[tag_key]
            deployed_values = deployed_tag_mapper[tag_key]

            values_to_add = new_values.difference(deployed_values)
            values_to_delete = deployed_values.difference(new_values)

            kwargs = dict(
                CatalogId=self.account_id,
                TagKey=tag_key,
            )

            if len(values_to_add):
                kwargs["TagValuesToAdd"] = list(values_to_add)

            if len(values_to_delete):
                kwargs["TagValuesToDelete"] = list(values_to_delete)

            if len(values_to_add) >= 1 or len(values_to_delete) >= 1:
                to_update_tag_kwargs.append(kwargs)

        if len(to_create_tag_kwargs):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Create tags ..."
            logger.show(msg)

        for kwargs in to_create_tag_kwargs:
            msg = f"{Fore.GREEN}+ [Create Tag] {Style.RESET_ALL}{kwargs['TagKey']!r}"
            logger.show(msg)
            msg = f"- values: {kwargs['TagValues']!r}"
            logger.show(msg, indent=1)

            if dry_run is False:
                self.lf_client.create_lf_tag(**kwargs)

        if len(to_update_tag_kwargs):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Update tags ..."
            logger.show(msg)

        for kwargs in to_update_tag_kwargs:
            msg = f"{Fore.BLUE}~ [Update Tag] {Style.RESET_ALL}{kwargs['TagKey']!r}"
            logger.show(msg)

            if kwargs.get("TagValuesToAdd", list()):
                msg = f"{Fore.GREEN}+ values to add{Fore.RESET}: {kwargs['TagValuesToAdd']!r}"
                logger.show(msg, indent=1)

            if kwargs.get("TagValuesToDelete", list()):
                msg = f"{Fore.RED}- values to delete{Fore.RESET}: {kwargs['TagValuesToDelete']!r}"
                logger.show(msg, indent=1)

            if dry_run is False:
                self.lf_client.update_lf_tag(**kwargs)

        if len(to_delete_tag_kwargs):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Delete tags ..."
            logger.show(msg)

        for kwargs in to_delete_tag_kwargs:
            msg = "{red}- [Delete Tag] {reset}{key!r}".format(
                red=Fore.RED,
                reset=Style.RESET_ALL,
                key=kwargs["TagKey"],
            )
            logger.show(msg)
            if dry_run is False:
                self.lf_client.delete_lf_tag(**kwargs)

        logger.enable_verbose = True

    def apply_resources(
        self,
        verbose=True,
        dry_run=False,
    ):
        """
        Ref:

        - Add: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.add_lf_tags_to_resource
        - Remove: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.remove_lf_tags_from_resource
        - Get: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.get_resource_lf_tags

        :param verbose:
        :param dry_run:
        :return:
        """
        if not verbose:
            logger.enable_verbose = False

        new_ra_mapper = self.resource_attachment_mapper
        deployed_ra_mapper = self.deployed_pb.resource_attachment_mapper

        (
            to_add_ra_id_set,
            to_remove_ra_id_set,
            _,
        ) = get_diff_and_inter(new_ra_mapper, deployed_ra_mapper)

        to_add_kwargs_list: List[dict] = list()
        to_remove_kwargs_list: List[dict] = list()

        for ra_id in to_add_ra_id_set:
            ra = new_ra_mapper[ra_id]
            kwargs = dict(
                CatalogId=self.account_id,
                LFTags=[
                    dict(
                        CatalogId=self.account_id,
                        TagKey=ra.tag.key,
                        TagValues=[ra.tag.value, ],
                    )
                ]
            )
            kwargs["Resource"] = {
                ra.resource.get_add_remove_lf_tags_arg_name: ra.resource.get_add_remove_lf_tags_arg_value
            }
            to_add_kwargs_list.append(kwargs)

        for ra_id in to_remove_ra_id_set:
            ra = deployed_ra_mapper[ra_id]
            kwargs = dict(
                CatalogId=self.account_id,
                LFTags=[
                    dict(
                        CatalogId=self.account_id,
                        TagKey=ra.tag.key,
                        TagValues=[ra.tag.value, ],
                    )
                ]
            )
            kwargs["Resource"] = {
                ra.resource.get_add_remove_lf_tags_arg_name: ra.resource.get_add_remove_lf_tags_arg_value
            }
            to_remove_kwargs_list.append(kwargs)

        if len(to_add_kwargs_list):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Attach tags ..."
            logger.show(msg)

        for kwargs in to_add_kwargs_list:
            msg = f"{Fore.GREEN}+ [Attach Tag] {Style.RESET_ALL}{{{kwargs['LFTags'][0]['TagKey']!r}: {kwargs['LFTags'][0]['TagValues'][0]}}} to {kwargs['Resource']}"
            logger.show(msg)

            if dry_run is False:
                self.lf_client.add_lf_tags_to_resource(**kwargs)

        if len(to_remove_kwargs_list):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Detach tags ..."
            logger.show(msg)

        for kwargs in to_remove_kwargs_list:
            msg = f"{Fore.RED}- [Detach Tag] {Style.RESET_ALL}{{{kwargs['LFTags'][0]['TagKey']!r}: {kwargs['LFTags'][0]['TagValues'][0]}}} from {kwargs['Resource']}"
            logger.show(msg)

            if dry_run is False:
                self.lf_client.remove_lf_tags_from_resource(**kwargs)

        logger.enable_verbose = True

    def apply_principals(
        self,
        verbose=True,
        dry_run=False,
    ):
        """

        :param verbose:
        :param dry_run:
        :return:
        """
        if not verbose:
            logger.enable_verbose = False

        new_pa_mapper = self.principal_attachment_mapper
        deployed_pa_mapper = self.deployed_pb.principal_attachment_mapper

        (
            to_grant_pa_id_set,
            to_revoke_pa_id_set,
            _,
        ) = get_diff_and_inter(new_pa_mapper, deployed_pa_mapper)

        # we use batch grant / revoke API
        to_grant_entry_list: List[dict] = list()
        to_revoke_entry_list: List[dict] = list()

        # aggregate by principal and tag and resource type
        to_grant_pa_by_principal_and_tag_and_resource_type: Dict[str, List[PrincipalAttachment]] = dict()
        for pa_id in to_grant_pa_id_set:
            pa = new_pa_mapper[pa_id]
            key = f"{pa.principal.id}{DELIMITER}{pa.tag.id}{DELIMITER}{pa.permission.resource_type}"
            try:
                to_grant_pa_by_principal_and_tag_and_resource_type[key].append(pa)
            except KeyError:
                to_grant_pa_by_principal_and_tag_and_resource_type[key] = [pa, ]

        for _, pa_list in to_grant_pa_by_principal_and_tag_and_resource_type.items():
            pa = pa_list[0]
            entry = dict(
                Id=str(uuid.uuid4()),
                Principal=dict(
                    DataLakePrincipalIdentifier=pa.principal.id,
                ),
                Resource=dict(
                    LFTagPolicy=dict(
                        CatalogId=self.account_id,
                        ResourceType=pa.permission.resource_type,
                        Expression=[
                            dict(
                                TagKey=pa.tag.key,
                                TagValues=[pa.tag.value, ],
                            )
                        ]
                    )
                ),
            )
            permissions = [
                pa.permission.permission
                for pa in pa_list
                if pa.permission.grantable is False
            ]
            permissions_with_grant_option = [
                pa.permission.permission
                for pa in pa_list
                if pa.permission.grantable is True
            ]
            if len(permissions):
                entry["Permissions"] = permissions
            if len(permissions_with_grant_option):
                entry["PermissionsWithGrantOption"] = permissions_with_grant_option

            permissions_in_message = ", ".join([
                pa.permission.id
                for pa in pa_list
            ])
            msgs = [
                f"{Fore.GREEN}- [Grant Permission] {Style.RESET_ALL}{pa.principal.id} {{{pa.tag.key!r}: {pa.tag.value!r}}} {permissions_in_message}"
            ]
            entry["_msgs"] = msgs
            to_grant_entry_list.append(entry)

        # aggregate by principal and tag and resource type
        to_revoke_pa_by_principal_and_tag_and_resource_type: Dict[str, List[PrincipalAttachment]] = dict()
        for pa_id in to_revoke_pa_id_set:
            pa = deployed_pa_mapper[pa_id]
            key = f"{pa.principal.id}{DELIMITER}{pa.tag.id}{DELIMITER}{pa.permission.resource_type}"
            try:
                to_revoke_pa_by_principal_and_tag_and_resource_type[key].append(pa)
            except KeyError:
                to_revoke_pa_by_principal_and_tag_and_resource_type[key] = [pa, ]

        for _, pa_list in to_revoke_pa_by_principal_and_tag_and_resource_type.items():
            pa = pa_list[0]
            entry = dict(
                Id=str(uuid.uuid4()),
                Principal=dict(
                    DataLakePrincipalIdentifier=pa.principal.id,
                ),
                Resource=dict(
                    LFTagPolicy=dict(
                        CatalogId=self.account_id,
                        ResourceType=pa.permission.resource_type,
                        Expression=[
                            dict(
                                TagKey=pa.tag.key,
                                TagValues=[pa.tag.value, ],
                            )
                        ]
                    )
                ),
            )
            permissions = [
                pa.permission.permission
                for pa in pa_list
                if pa.permission.grantable is False
            ]
            permissions_with_grant_option = [
                pa.permission.permission
                for pa in pa_list
                if pa.permission.grantable is True
            ]
            if len(permissions):
                entry["Permissions"] = permissions
            if len(permissions_with_grant_option):
                entry["PermissionsWithGrantOption"] = permissions_with_grant_option

            permissions_in_message = ", ".join([
                pa.permission.id
                for pa in pa_list
            ])
            msgs = [
                f"{Fore.RED}- [Revoke Permission] {Style.RESET_ALL}{pa.principal.id} {{{pa.tag.key!r}: {pa.tag.value!r}}} {permissions_in_message}"
            ]
            entry["_msgs"] = msgs
            to_revoke_entry_list.append(entry)

        if len(to_grant_entry_list):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Grant permissions ..."
            logger.show(msg)

        for to_grant_entry_sub_list in grouper_list(to_grant_entry_list, 20):
            for entry in to_grant_entry_sub_list:
                msgs = entry.pop("_msgs")
                for msg in msgs:
                    logger.show(msg)

            if dry_run is False:
                self.lf_client.batch_grant_permissions(
                    CatalogId=self.account_id,
                    Entries=to_grant_entry_sub_list
                )

        if len(to_revoke_entry_list):
            msg = f"{Fore.CYAN}[Info] {Style.RESET_ALL}Revoke permissions ..."
            logger.show(msg)

        for to_revoke_entry_sub_list in grouper_list(to_revoke_entry_list, 20):
            for entry in to_revoke_entry_sub_list:
                msgs = entry.pop("_msgs")
                for msg in msgs:
                    logger.show(msg)

            if dry_run is False:
                self.lf_client.batch_revoke_permissions(
                    CatalogId=self.account_id,
                    Entries=to_revoke_entry_sub_list
                )

        logger.enable_verbose = True

    def load_deployed_playbook(self):
        if self.p_deployed.exists():
            self.deployed_pb = Playbook.deserialize(
                json.loads(self.p_deployed.read_text())
            )
        else:
            self.deployed_pb = Playbook(_skip_validation=True)
            self.p_deployed.write_text(
                json.dumps(self.deployed_pb.serialize(), indent=4)
            )

    def apply(
        self,
        verbose=True,
        dry_run=False,
    ):
        self.load_deployed_playbook()
        self.apply_tags(verbose=verbose, dry_run=dry_run)
        self.apply_resources(verbose=verbose, dry_run=dry_run)
        self.apply_principals(verbose=verbose, dry_run=dry_run)

        # pb = self.from
        if dry_run is False:
            self.p_deployed.write_text(json.dumps(self.serialize(), indent=4))
