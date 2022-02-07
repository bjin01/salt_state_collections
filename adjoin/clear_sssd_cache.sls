clear_sssd_cache_sls:
  cmd.script:
    - name: clear_sssd_cache_sls
    - source: salt://adjoin/configs/clear_sssd_cache.sh
    
