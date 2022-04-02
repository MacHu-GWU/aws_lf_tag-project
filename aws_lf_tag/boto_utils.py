# -*- coding: utf-8 -*-

from typing import List, Dict
import attr
from attrs_mate import AttrsClass


def is_tag_exists(
    lf_client,
    account_id: str,
    key: str,
) -> bool:
    """
    Check if an Lake Formation tag exists or not

    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.get_lf_tag
    """
    try:
        lf_client.get_lf_tag(CatalogId=account_id, TagKey=key)
        return True
    except Exception as e:
        if str(e).endswith("GetLFTag operation: Tag key does not exist"):
            return False
        else:
            raise e


@attr.define
class LFTag(AttrsClass):
    CatalogId: str = AttrsClass.ib_str(nullable=False)
    TagKey: str = AttrsClass.ib_str(nullable=False)
    TagValues: List[str] = AttrsClass.ib_list_of_str(nullable=False)


def list_tag(
    lf_client,
    catalog_id: str,
    resource_share_type: str = "ALL",
) -> Dict[str, LFTag]:
    """
    Call ``list_lf_tags`` api recursively to get all lakeformation tags.

    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.list_lf_tags
    """
    next_token = None
    tags: Dict[str, LFTag] = dict()
    while 1:
        kwargs = dict(
            CatalogId=catalog_id,
            ResourceShareType=resource_share_type,
            MaxResults=1000,
        )
        if next_token:
            kwargs["NextToken"] = next_token
        res = lf_client.list_lf_tags(**kwargs)
        for dct in res.get("LFTags", list()):
            lf_tag = LFTag.from_dict(dct)
            tags[lf_tag.TagKey] = lf_tag
        next_token = res.get("NextToken")
        if next_token is None:
            break

    return tags


def create_tag(
    lf_client,
    account_id: str,
    key: str,
    values: List[str],
) -> dict:
    """
    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.create_lf_tag
    """
    return lf_client.create_lf_tag(
        CatalogId=account_id,
        TagKey=key,
        TagValues=values,
    )


def update_tag(
    lf_client,
    account_id: str,
    key: str,
    values_to_delete: List[str],
    values_to_add: List[str],
) -> dict:
    """
    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.update_lf_tag
    """
    return lf_client.create_lf_tag(
        CatalogId=account_id,
        TagKey=key,
        TagValuesToDelete=values_to_delete,
        TagValuesToAdd=values_to_add,
    )


def delete_tag(
    lf_client,
    account_id: str,
    key: str,
) -> dict:
    """
    Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lakeformation.html#LakeFormation.Client.delete_lf_tag
    """
    return lf_client.delete_lf_tag(
        CatalogId=account_id,
        TagKey=key,
    )
