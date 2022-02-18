# -*- coding: utf-8 -*-

from aws_lf_tag import Database, Table, Column

{% if database_list|length %}
account_id = "{{ database_list[0].account_id }}"
region = "{{ database_list[0].region }}"
{% endif %}

{% for database in database_list %}
{{ database.render_define() }}

{% for table in database.t.values() %}
{{ table.render_define() }}

{% for column in table.c.values() %}
{{ column.render_define() }}
{% endfor %}

{% endfor %}

{% endfor %}
