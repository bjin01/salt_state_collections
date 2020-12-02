{% set meineumgebung = salt['grains.get']('umgebung', 'dev') %}

{% if meineumgebung  == 'qas' %}
meinesoftware:
  pkg.installed:
    - pkgs:
      - wget
      - curl
      - mc

{% endif %}



