# -*- coding: utf-8 -*-

from typing import List, Dict


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
