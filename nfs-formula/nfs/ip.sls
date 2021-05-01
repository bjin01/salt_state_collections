{% set sid = "xyz" %}
{% set data = [] %}
{% set shared = [] %}

{% set match_data = "_" + sid + "_data" %}
{% set match_shared = "_" + sid + "_shared" %}

{% for h, i in salt['pillar.get']('nas_ip').items() %}
{% if match_data in h %}
{% do data.append(i) %}
{% endif %}
{% endfor %}

{% for h, i in salt['pillar.get']('nas_ip').items() %}
{% if match_shared in h %}
{% do shared.append(i) %}
{% endif %}
{% endfor %}

afasdfaf:
  cmd.run:
    - name: echo "{{ data[0] }} ----------- {{ shared[0] }}"

