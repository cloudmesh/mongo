from cmd3.shell import command
from cloudmesh_common.logger import LOGGER
import cloudmesh
import time
from pprint import pprint
import os
import yaml
import json

# Hello World
print ("Hello, World!")

# Reading yaml file for configuration
with open('mongo-config.yaml', 'r') as f:
    doc = yaml.load(f)

cloud_name = doc["setup"]["cloud"]
project = doc["setup"]["project"]
group_name = doc["user"]["cluster_groupname"]
login_name = doc["user"]["login_name"]
flavor = doc["user"]["flavor"]
count = doc["user"]["count"]
image = doc["user"]["image"]

data = {"groupname": group_name,
        "cloud": cloud_name,
        "project": project,
        "login": login_name,
        "flavor": flavor,
        "count": count,
        "image": image}
pprint(data)

cloudmesh.shell("cloud on {cloud}".format(**data))
cloudmesh.shell("cloud select {cloud}".format(**data))
cloudmesh.shell("project default {project}".format(**data))

result = cloudmesh.shell('cluster create '
                         ' --force'
                         ' --count={count}'
                         ' --group={groupname}'
                         ' --ln={login}'
                         ' --cloud={cloud}'
                         ' --flavor={flavor}'
                         ' --image={image}'.format(**data))
pprint(result)

# Display the list of all the VMs in the group
json_data = cloudmesh.shell('group show {groupname} --format=json'.format(**data))
pprint(json_data)
data = json.loads(json_data.replace('\r\n', '\\r\\n'))
vm_list = data["VM"]
data_vm_list  = {"vm_list":vm_list}
pprint(vm_list)

# Display all the Public IP of the VMs
json_data = cloudmesh.shell('vm ip show --names={vm_list} --format=json'.format(**data_vm_list))
data = json.loads(json_data.replace('\r\n', '\\r\\n'))
ip_list=str(data)
pprint(ip_list)

#Delete the group and the VMs in it
cloudmesh.shell('vm delete --cloud={cloud} --group={groupname} --force'.format(**data))
