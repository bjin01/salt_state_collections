resend_file:
  local.cmd.run:
    - tgt: {{ data['id'] }} 
    - arg: 
      - salt-call state.sls_id config_files_mycnf manager_org_1.server_role_mariadb


 
