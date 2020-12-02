{% set found = {'gefunden': False} %}
{% set list = salt['grains.get']('installed_products') -%}
{% for i in list -%}
  {% if "containers" in i -%}
    {% if found.update({'gefunden': True}) %}
      {% do salt.log.error(found) %}
    {% endif %}
  {% endif %}
{% endfor %}
{% if found['gefunden'] -%}
sysstat:
  pkg.installed
{% endif %}



