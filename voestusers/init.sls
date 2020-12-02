sapsys:
  group.present:
    - gid: 3000

{% for user, args in salt['pillar.get']('users', {}).items() %}
{{ user }}:
  user.present:
    - fullname: {{ args['name'] }} 
    - password: {{ args['pwd'] }}
    - shell: /bin/{{ args['shell'] }}
    - createhome: True
    - home: /home/{{ user }}
    - uid: {{ args['uid'] }}
    - groups:
      - wheel
      - {{ args['grpname'] }}
    - require:
      - group: sapsys
{% endfor %}

{% for user in salt['pillar.get']('delete_users', []) %}
{{ user }}:
  user.absent:
    - purge: True
    - force: True
{% endfor %}
