{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set mystring = '-release' %}
{% set release_list = [] %}
{% set product_list = salt.cmd.run('rpm -qa ').split('\n') -%}
{% for i in product_list -%}
  {% if mystring in i %}
    {% set tempname = i.split(mystring) %}
    {% do release_list.append(tempname[0]) %}
  {% endif %}
{% endfor %}

set_product_grains:
  grains.list_present:
    - name: installed_products
    - value: {{ release_list }}
