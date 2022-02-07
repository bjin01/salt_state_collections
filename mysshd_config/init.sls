zzz_sshd_no_root_login:
  file.keyvalue:
    - name: /etc/ssh/sshd_config
    - key_values:
        permitrootlogin: 'no'
        PasswordAuthentication: 'no'
        PubkeyAuthentication: 'yes'
    - separator: ' '
    - uncomment: '#'
    - key_ignore_case: True
    - append_if_not_found: True

zzz_sshd_service:
  service.running:
    - name: sshd
    - enable: True
    - watch:
      - file: zzz_sshd_no_root_login
 
