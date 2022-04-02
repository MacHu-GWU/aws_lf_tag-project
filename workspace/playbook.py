# -*- coding: utf-8 -*-

import boto3
from pathlib_mate import Path
from rich import print
import aws_lf_tag as lf
import resource_669508176277_us_west_1 as r
import principal_669508176277 as p

profile_name = "aws_data_lab_sanhe"
region_name = "us-west-1"
boto_ses = boto3.session.Session(profile_name=profile_name, region_name=region_name)
dir_here = Path.dir_here(__file__)
pb = lf.Playbook(boto_ses=boto_ses, workspace_dir=dir_here.abspath)

# ------------------------------------------------------------------------------
# Tag
# ------------------------------------------------------------------------------
prefix = "aws_lf_tag"

# tag_admin_access_y = lf.Tag(key=f"{prefix}_admin_access", value="y", pb=pb)
# tag_admin_access_n = lf.Tag(key=f"{prefix}_admin_access", value="n", pb=pb)
# tag_regular_access_y = lf.Tag(key=f"{prefix}_regular_access", value="y", pb=pb)
# tag_regular_access_n = lf.Tag(key=f"{prefix}_regular_access", value="n", pb=pb)
# tag_limited_access_y = lf.Tag(key=f"{prefix}_limited_access", value="y", pb=pb)
# tag_limited_access_n = lf.Tag(key=f"{prefix}_limited_access", value="n", pb=pb)

# ------------------------------------------------------------------------------
# Resource
#
# all database name / table name / column name are automatically generated
# you can leverage text editor auto complete feature in
# VScode / Sublime / PyCharm / Notepad ++ or any
# to access a resource variable
# ------------------------------------------------------------------------------
# tag_admin_access_y.attach_to_resource(r.db_669508176277__us_west_1__lf_sme_demo_db)
#
# tag_regular_access_y.attach_to_resource(r.db_669508176277__us_west_1__lf_sme_demo_db)
# tag_regular_access_n.attach_to_resource(r.col_669508176277__us_west_1__lf_sme_demo_db__users__ssn)
#
# tag_limited_access_y.attach_to_resource(r.db_669508176277__us_west_1__lf_sme_demo_db)
# tag_limited_access_n.attach_to_resource(r.tb_669508176277__us_west_1__lf_sme_demo_db__items)

# ------------------------------------------------------------------------------
# Principal
#
# all IAM user / role principal are automatically generated
# same as resource, you can leverage text editor auto complete feature
# ------------------------------------------------------------------------------
# tag_admin_access_y.attach_to_principal(p.role_lf_sme_demo_admin, permissions=[lf.SuperDatabase, lf.SuperDatabaseGrantable, lf.SuperTable, lf.SuperTableGrantable])
# tag_regular_access_y.attach_to_principal(p.role_lf_sme_demo_regular, permissions=[lf.DescribeDatabase, lf.DescribeTable, lf.Select])
# tag_limited_access_y.attach_to_principal(p.role_lf_sme_demo_limited, permissions=[lf.DescribeDatabase, lf.DescribeTable, lf.Select])


# ------------------------------------------------------------------------------
# Apply all change
# ------------------------------------------------------------------------------
data = pb.serialize()
# print(data)
pb.apply(verbose=True, dry_run=False)
# print(pb.region)
