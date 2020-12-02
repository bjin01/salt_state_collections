{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set testlist = ['product1', 'product2', 'product3'] %}
{% set mystring = 'release' %}
{% set release_list = [] %}
{% set product_list = salt.cmd.run('rpm -qa') %}
{% for product_name in product_list %}
{% if mystring in product_name %}
    {% do release_list.append(mystring) %} 
{% endif %}
{% endfor %}

set_product_grains:
  grains.list_present:
    - name: installed_products
    - value: {{ testlist }}
