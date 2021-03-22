{% from "mygpgkeys/map.jinja" import mygpg with context %}
{% for k, i in mygpg.items() %}
key_{{ k }}:
  cmd.run:
    - name: rpm --import http://suma1.bo2go.home/pub/{{ i }}
{% endfor %}

