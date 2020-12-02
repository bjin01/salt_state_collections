sapsys:
  group.present:
    - gid: 3000

{% for user, args in salt['pillar.get']('users', {}).iteritems() %}
{{ user }}:
  user.present:
    - fullname: {{ args['name'] }} 
    - password: {{ args['pwd'] }}
    - shell: {{ args['shell'] }}
    - createhomeTrue: True
    - home: /home/{{ user }}
    - uid: {{ args['uid'] }}
    - groups:
      - wheel
      - {{ args['grpname'] }}
    - require:
      - group: sapsys
{% endfor %}

