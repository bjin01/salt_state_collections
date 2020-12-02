{% set docker_images = salt.cmd.shell("docker image ls | awk NR\>1 | awk '{ print $1 }' | uniq").split('\n') %}
docker_images:
  grains.list_present:
    - name: docker_images
    - value: {{ docker_images }}

