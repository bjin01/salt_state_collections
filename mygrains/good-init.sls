{% set mykernel = salt.cmd.run('uname -r') %}
set_grains:
  grains.present:
    - name: kernel_value
    - value: {{ mykernel }}
    - force: True

{% set release_list = [] %}
{% set product_list = salt.pkg.list_products() %}
{% for a in product_list %}
{% for i,k in a.items() %}
  {% if 'name' in i %}
    {% do release_list.append(k) %} 
  {% endif %}
{% endfor %}
{% endfor %}

set_product_grains:
  grains.present:
    - name: installed_products
    - value: {{ release_list }}
    - force: True
