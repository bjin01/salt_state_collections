{%- set keyfile = 'https://bjsuma.bo2go.home/pub/ptf-gpg-pubkey-b37b98a9.key'  %}
import_gpgkey:
  cmd.run:
    - name: /usr/bin/rpm --import {{ keyfile }}
 
 
