from cmd3.shell import command
from cloudmesh_common.logger import LOGGER
import cloudmesh
import time
from pprint import pprint
import os
import yaml
import json
import sys

class known_hosts(object):

    def __init__(self):
        self.filename = os.path.expanduser('~/.ssh/known_hosts')
        self.load()
        
    def delete(self, prefix):
        for key in self.keys:
            if key.startswith(prefix):
                ip = key.split()[0]
                print "Deleting:",  ip

    def load(self):
        with open(self.filename, 'r') as f:
            self.keys = f.read().split("\n")[:-1]

    def save(self):
        with open(self.filename, 'w') as f:
            for key in self.keys:
                f.write(key + "\n")

                
class deploy_mongo(object):

    def __init__(self, filename='mongo-config.yaml'):
        self.username = cloudmesh.load().username()
        with open(filename, 'r') as f:
            self.config = yaml.load(f)
        pprint (self.config)
        self.data = dict(self.config['config'].items() + self.config['cloud'].items())  
        self.data["groupname"] = self.username + '-' + self.config['config']['group_postfix']

    def _execute(self, commands):
        for command in commands:
            print "cm>", command
            r = cloudmesh.shell(command)
            print r
        
    def _prepare_cloudmesh(self):
        commands = [
            "cloud on {cloud}".format(**self.data),
            "cloud select {cloud}".format(**self.data),
            "project default {project}".format(**self.data)
        ]
        self._execute(commands)

    def _delete_cluster(self):
        commands = ['vm delete --cloud={cloud} --group={groupname} --force'.format(**self.data)]
        self._execute(commands)
                        
    def _create_cluster(self):
        commands = str('cluster create '
                      ' --force'
                      ' --count={count}'
                      ' --group={groupname}'
                      ' --ln={login}'
                      ' --cloud={cloud}'
                      ' --flavor={flavor}'
                      ' --image={image}'.format(**self.data))
        self._execute(commands)        

    def _vm_names_cluster(self):
        '''Display the list of all the VMs in the group'''
        command = 'group show {groupname} --format=json'.format(**self.data)
        print "cm>", command
        json_data = cloudmesh.shell(command)
        pprint(json_data)
        if not 'VM' in json_data:
            vm_list = []
        vms = json.loads(json_data.replace("\n"," "))            
        vm_list = vms["VM"]
        vm_list = [x.encode('UTF8') for x in vm_list]
        return vm_list

    def _ips_cluster(self):
        vms = self._vm_names_cluster()
        vms_string = ",".join(vms)
        command = 'vm ip show --names="{0}" --format=json'.format(vms_string)
        print "cm>", command
        json_data = cloudmesh.shell(command)
        ip_data = json.loads(json_data.replace('\n', ' '))
        return ip_data
        
#
# initialize
#

service = deploy_mongo()


print service.username
pprint(service.config)
pprint(service.data)

#
# prepare known hosts file
#
hosts = known_hosts()
hosts.delete('149')
hosts.save()

#
# prepare cloudmesh
#
service._prepare_cloudmesh()

#
# remove old clusters
#
service._delete_cluster()
service._create_cluster()

#
# get the ips
#
print service._vm_names_cluster()


pprint (service._ips_cluster())


sys.exit()




