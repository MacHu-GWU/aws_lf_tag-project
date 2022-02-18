# -*- coding: utf-8 -*-

from aws_lf_tag import IamUser, IamRole

{% for iam_user in iam_user_list %}
{{ iam_user.render_define() }}
{% endfor %}

{% for iam_role in iam_role_list %}
{{ iam_role.render_define() }}
{% endfor %}
