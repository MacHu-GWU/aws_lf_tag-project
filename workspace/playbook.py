# -*- coding: utf-8 -*-

import boto3
from rich import print
import aws_lf_tag as lf
import resource_669508176277_us_east_1 as r
import principal_669508176277 as p

profile_name = "aws_data_lab_sanhe"
region_name = "us-east-1"
boto_ses = boto3.session.Session(profile_name=profile_name, region_name=region_name)

pb = lf.Playbook(boto_ses=boto_ses)

# ------------------------------------------------------------------------------
# Tag
# ------------------------------------------------------------------------------
prefix = "aws_lf_tag"
tag_admin_access_y = lf.Tag(key=f"{prefix}_admin_access", value="y", pb=pb)
tag_admin_access_n = lf.Tag(key=f"{prefix}_admin_access", value="n", pb=pb)
tag_regular_access_y = lf.Tag(key=f"{prefix}_regular_access", value="y", pb=pb)
tag_regular_access_n = lf.Tag(key=f"{prefix}_regular_access", value="n", pb=pb)
tag_limited_access_y = lf.Tag(key=f"{prefix}_limited_access", value="y", pb=pb)
tag_limited_access_n = lf.Tag(key=f"{prefix}_limited_access", value="n", pb=pb)

# ------------------------------------------------------------------------------
# Resource
#
# all database name / table name / column name are automatically generated
# you can leverage text editor auto complete feature in
# VScode / Sublime / PyCharm / Notepad ++ or any
# to access a resource variable
# ------------------------------------------------------------------------------
r.db_669508176277__us_east_1__lf_sme_demo_db.attach(tag_admin_access_y)

r.db_669508176277__us_east_1__lf_sme_demo_db.attach(tag_regular_access_y)
r.col_669508176277__us_east_1__lf_sme_demo_db__users__ssn.attach(tag_regular_access_n)

r.db_669508176277__us_east_1__lf_sme_demo_db.attach(tag_limited_access_y)
r.tb_669508176277__us_east_1__lf_sme_demo_db__items.attach(tag_limited_access_n)
r.col_669508176277__us_east_1__lf_sme_demo_db__users__ssn.attach(tag_limited_access_n)
r.col_669508176277__us_east_1__lf_sme_demo_db__users__confidential.attach(tag_limited_access_n)

# print(r.db_669508176277__us_east_1__lf_sme_demo_db.tags)

# ------------------------------------------------------------------------------
# Principal
#
# all IAM user / role principal are automatically generated
# same as resource, you can leverage text editor auto complete feature
# ------------------------------------------------------------------------------
p.role_lf_sme_demo_admin.attach(tag_admin_access_y, permissions=[lf.SuperDatabase, lf.SuperTable])
p.role_lf_sme_demo_regular.attach(tag_regular_access_y, permissions=[lf.DescribeDatabase, lf.DescribeTable, lf.Select])
p.role_lf_sme_demo_limited.attach(tag_limited_access_y, permissions=[lf.DescribeDatabase, lf.DescribeTable, lf.Select])

# print(p.role_lf_sme_demo_admin.bindings)

# ------------------------------------------------------------------------------
# Apply all change
# ------------------------------------------------------------------------------
data = pb.serialize()
print(data)
# pb.apply()
