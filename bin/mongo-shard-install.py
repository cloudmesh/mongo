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
        commands = ['cluster create '
                    ' --force'
                    ' --count={count}'
                    ' --group={groupname}'
                    ' --ln={login}'
                    ' --cloud={cloud}'
                    ' --flavor={flavor}'
                    ' --image={image}'.format(**self.data)]
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
        command = 'vm ip show --names={0} --format=json'.format(vms_string)
        print "cm>", command
        json_data = cloudmesh.shell(command)
        ip_data = json.loads(json_data.replace('\n', ' '))
        pprint(ip_data)
        return ip_data
        
    def _ips_list(self):
        ip_data = self._ips_cluster()
        ip_list = ip_data["floating"]
        ip_list = [x.encode('UTF8') for x in ip_list]
        self.ip_list = ip_list
        counter = 0
        for ip in ip_list:	
            if counter <= 2:
                self.config_Server.append(ip)
            elif counter > 2 and counter <=4:
                self.router_server.append(ip)
            else:
                self.shard_server.append(ip)	
            counter = counter + 1
            
        print("List of config server")
        pprint(self.config_server)
        print("List of router server")
        pprint(self.router_server)
        print("List of shard server")
        pprint(self.shard_server)
        return ip_list
		
    def _install_mongo(self):
        print "Waiting for a minute to let VMs build and start"
        time.sleep(60)		
        # Install mongoDB on all the servers
        print("=====Installing MongoDB on all the VMs =====")
        script = """
        sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
        echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
        sudo apt-get update
        sudo apt-get install -y mongodb-org"""
        commands = script.split("\n")[1:]
        for ip in self.ip_list:
            result = mesh.wait(ipaddr=ip, interval=10, retry=10)
            print (result)
            for command in commands:
                print ('>execute', command)		
                mesh.ssh_execute(ipaddr=ip, command=command)
				
    def _setup_mongo_configServer(self):
        print("=====Setting up Config Server=====")
        script = """
        sudo mkdir ~/mongo-metadata
        sudo mkdir ~/mongo-log
        sudo mongod --fork --configsvr --dbpath ~/mongo-metadata --logpath ~/mongo-log/log.data --port 27019"""
        commands = script.split("\n")[1:]
        for ip in self.config_server:
            result = mesh.wait(ipaddr=ip, interval=10, retry=10)
            print (result)
            for command in commands:
                print ('>execute', command)		
                mesh.ssh_execute(ipaddr=ip, command=command)
                
    def _setup_mongo_routerServer(self):
        # Setup Router Server
        print("=====Setting up Query Router=====")
        port = ":27019"
        ip_list = self.shard_server[0] + "," + self.shard_server[1] + "," + self.shard_server[2]  + "," + self.shard_server[3]
        config_command = "sudo mongos --fork --logpath ~/mongo-log/log.data --bind_ip " + ip_list + " --configdb " + self.config_server[0] + port + "," + self.config_server[1] + port + "," + self.config_server[2] + port
        for ip in Router_Server:
            result = mesh.wait(ipaddr=ip, interval=10, retry=10)
            print (result)
            print ('>execute', 'sudo mkdir ~/mongo-log')	
            mesh.ssh_execute(ipaddr=ip, command='sudo mkdir ~/mongo-log')
            print ('>execute', config_command)	
            mesh.ssh_execute(ipaddr=ip, command=config_command)
		
        
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
pprint (service._ips_list())

sys.exit()