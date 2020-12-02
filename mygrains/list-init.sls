{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set mystring = 'release' %}
{% set release_list = [] %}
{% set product_list = salt.cmd.run('rpm -qa | grep release').replace('\n', ':') -%}
{% for product_name in product_list -%}
    {% do release_list.append(product_name) -%}
{% endfor %}

set_product_grains:
  grains.present:
    - name: installed_products
    - value: {{ release_list }}
