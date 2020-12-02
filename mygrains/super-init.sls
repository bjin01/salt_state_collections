{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set mystring = 'release' %}
{% set release_list = [] %}
{% set product_list = salt.cmd.run('rpm -qa | grep release').replace('\n', ':') -%}
{% set new_list = product_list.split(':') -%}
{% for i in new_list -%}
  {% if mystring in i %}
    {% do release_list.append(i) %}
  {% endif %}
{% endfor %}

set_product_grains:
  grains.present:
    - name: installed_products
    - value: {{ release_list }}
    - force: True
