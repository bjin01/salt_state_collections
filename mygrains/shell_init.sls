{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}

{% set product_list = salt.cmd.shell('rpm -qa | grep release').split('\n') -%}

set_product_grains:
  grains.list_present:
    - name: installed_products
    - value: {{ product_list }}
