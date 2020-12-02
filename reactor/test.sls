reapply_mariadb:
  local.state.apply:
    - tgt: {{ data['id'] }}
    - arg:
      - manager_org_1.server_role_mariadb.sls

