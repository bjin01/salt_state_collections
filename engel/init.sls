standard-sw:
  pkg.installed:
    - pkgs:
      - {{ pillar['webserver'] }}
      - sg3_utils
      - vim
 
verbotene-sw:
  pkg.removed:
    - pkgs:
      - name: nginx
 
