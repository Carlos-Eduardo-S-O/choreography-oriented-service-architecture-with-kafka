import os

container_name = "services_checktoken_1"

command = f"docker container exec -it {container_name} bash -c 'python3 panel.py'"
os.system(command)



