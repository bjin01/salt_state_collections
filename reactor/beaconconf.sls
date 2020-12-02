restart_minion:
  local.cmd.run:
    - tgt: {{ data['id'] }} 
    - arg: 
      - systemctl restart salt-minion.service 

