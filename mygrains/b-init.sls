{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set product_list = salt.cmd.run('rpm -qa | grep release', []) %}
{% for product_name in product_list %}
set_product_grains:
  grains.present:
    - name: installed_myproducts
    - value: {{ product_name }}
{% endfor %}
