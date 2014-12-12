from cmd3.shell import command
from cloudmesh_common.logger import LOGGER
import cloudmesh
import time
from pprint import pprint
import os


# Hello World
print ("Hello, World!")

#Activate user on cloudmesh
mesh = cloudmesh.mesh("mongo")
username = cloudmesh.load().username()
mesh.activate(username)
print (username)


#Set the default flavor and image for VM creation
cloud = 'india'
flavor = mesh.flavor('india', 'm1.medium')
image=mesh.image('india','fg452/rsinghania-001/my-ubuntu-01')
defaults = mesh.default('india', 'image', image)
defaults = mesh.default('india', 'flavor', flavor)

#start 9 VMs : For setting sharding in MongoDB
# 3 Config Server, 2 Query Routers, 4 Shard Servers
print ("Firing 9 VMs for setting up sharded MongoDB")
Server_IPs = []
for x in range(9):
	result = mesh.start(cloud='india', cm_user_id=username, flavor=flavor, image=image)
	pprint (result)
	server = result['server']['id']
	pprint (result['name'])
	ip=mesh.assign_public_ip('india', server, username)
	Server_IPs.append(ip)

#print all IPs 
Config_Server = []
Router_Server = []
Shard_Server = []

counter = 0
for ip in Server_IPs:	
	command = 'ssh-keygen -R ' + ip
	os.system(command)
	if counter <= 2:
		Config_Server.append(ip)
	elif counter > 2 and counter <=4:
		Router_Server.append(ip)
	else:
		Shard_Server.append(ip)	
	counter = counter + 1
	
print ("==============Printing IPs for Config Servers============")
for ip in Config_Server:
	print ip

print ("==============Printing IPs for Query Router==============")
for ip in Router_Server:
	print ip

print ("==============Printing IPs for Shard Server==============")
for ip in Shard_Server:
	print ip


# Wait for a minute for all the Vms to build and start
print "Waiting for a minute to let VMs build and start"
time.sleep(60)

# Install mongoDB on all the servers
print("=====Installing MongoDB on all the VMs and enable ubuntu firewall for connection to mongoDB instance=====")
script = """
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update
sudo apt-get install -y mongodb-org"""

commands = script.split("\n")[1:]
for ip in Server_IPs:
	result = mesh.wait(ipaddr=ip, interval=10, retry=10)
	print (result)
	for command in commands:
		print ('>execute', command)		
		mesh.ssh_execute(ipaddr=ip, command=command)


# Setup Config server
print("=====Setting up Config Server=====")
script = """
sudo mkdir ~/mongo-metadata
sudo mkdir ~/mongo-log
sudo mongod --fork --configsvr --dbpath ~/mongo-metadata --logpath ~/mongo-log/log.data --port 27019"""
commands = script.split("\n")[1:]
for ip in Config_Server:
	result = mesh.wait(ipaddr=ip, interval=10, retry=10)
	print (result)
	for command in commands:
		print ('>execute', command)		
		mesh.ssh_execute(ipaddr=ip, command=command)

# Setup Router Server
print("=====Setting up Query Router=====")
port = ":27019"
ip_list = Shard_Server[0] + "," + Shard_Server[1] + "," + Shard_Server[2]  + "," + Shard_Server[3]
config_command = "sudo mongos --fork --logpath ~/mongo-log/log.data --bind_ip " + ip_list + " --configdb " + Config_Server[0] + port + "," + Config_Server[1] + port + "," + Config_Server[2] + port
for ip in Router_Server:
	result = mesh.wait(ipaddr=ip, interval=10, retry=10)
	print (result)
	print ('>execute', 'sudo mkdir ~/mongo-log')	
	mesh.ssh_execute(ipaddr=ip, command='sudo mkdir ~/mongo-log')
	print ('>execute', config_command)	
	mesh.ssh_execute(ipaddr=ip, command=config_command)