# -*- coding: utf-8 -*-

from aws_lf_tag import Database, Table, Column


account_id = "669508176277"
region = "us-west-1"



db_669508176277__us_west_1__lf_sme_demo_db = Database(account_id=account_id, region=region, name="lf_sme_demo_db")


tb_669508176277__us_west_1__lf_sme_demo_db__items = Table(name="items", database=db_669508176277__us_west_1__lf_sme_demo_db)


col_669508176277__us_west_1__lf_sme_demo_db__items__item_id = Column(name="item_id", table=tb_669508176277__us_west_1__lf_sme_demo_db__items)

col_669508176277__us_west_1__lf_sme_demo_db__items__item_name = Column(name="item_name", table=tb_669508176277__us_west_1__lf_sme_demo_db__items)

col_669508176277__us_west_1__lf_sme_demo_db__items__price = Column(name="price", table=tb_669508176277__us_west_1__lf_sme_demo_db__items)



tb_669508176277__us_west_1__lf_sme_demo_db__orders = Table(name="orders", database=db_669508176277__us_west_1__lf_sme_demo_db)


col_669508176277__us_west_1__lf_sme_demo_db__orders__order_id = Column(name="order_id", table=tb_669508176277__us_west_1__lf_sme_demo_db__orders)

col_669508176277__us_west_1__lf_sme_demo_db__orders__buyer_id = Column(name="buyer_id", table=tb_669508176277__us_west_1__lf_sme_demo_db__orders)

col_669508176277__us_west_1__lf_sme_demo_db__orders__items = Column(name="items", table=tb_669508176277__us_west_1__lf_sme_demo_db__orders)



tb_669508176277__us_west_1__lf_sme_demo_db__users = Table(name="users", database=db_669508176277__us_west_1__lf_sme_demo_db)


col_669508176277__us_west_1__lf_sme_demo_db__users__user_id = Column(name="user_id", table=tb_669508176277__us_west_1__lf_sme_demo_db__users)

col_669508176277__us_west_1__lf_sme_demo_db__users__email = Column(name="email", table=tb_669508176277__us_west_1__lf_sme_demo_db__users)

col_669508176277__us_west_1__lf_sme_demo_db__users__ssn = Column(name="ssn", table=tb_669508176277__us_west_1__lf_sme_demo_db__users)

col_669508176277__us_west_1__lf_sme_demo_db__users__confidential = Column(name="confidential", table=tb_669508176277__us_west_1__lf_sme_demo_db__users)




