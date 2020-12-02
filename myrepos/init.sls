{% from "myrepos/map.jinja" import repo with context %}

myrepofile:
  file.managed:
    - name: {{ repo.repofile }}
    - source: salt://myrepos/opensuserepo.repo
    - template: jinja

