{% set mylist =  ['product1', 'product2', 'product3'] %}
set_myproduct_grains:
  grains.list_present:
    - name: installed_myproducts
    - value: {{ mylist }}

