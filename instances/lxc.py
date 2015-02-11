import os
import signal
import subprocess
import sys

from subprocess import Popen, PIPE


'''
	General maintenance calls inside LXContainer

	- create():             create new LXC
	- exists():             check if LXC exists
	- get_running():        get list of all running LXCs
	- get_stopped():        get list of all stopped LXCs
	- get_frozen():         get list of all frozen LXCs
	- get_by_status():  get list of all LXCs of a certain status
	- get_all():            get list of all LXCs
	- start():              start a stopped container
	- stop():               stop a running container
	- kill():               send kill signal to process 1 of container
	- destroy():            removes container
	- shutdown():           shut-down container
	- freeze():             freeze a container
	- unfreeze():           unfreeze a container
'''

class lxcman(object):
	
	def __init__(self, logging=True):
		self.logging = logging
	
	
	def logSelf(self, x):
		if self.logging:
			print x
		else:
			pass


	def create(self, name, cfgFile=None, template=None, backStore=None, templateOptions=None):
		self.logSelf('Trying to create %s' % name)
		if self.exists(name):
			return
		else:
			try:
				cmd = ['lxc-create', '-n', name]
				
				if cfgFile:
					cmd.append('-f')
					cmd.append(cfgFile)
				if template:
					cmd.append('-t')
					cmd.append(template)
				if backStore:
					cmd.append('-B')
					cmd.append(backStore)
				if templateOptions:
					cmd.append('--')
					cmd.append(templateOptions)
				
				self.logSelf('Running command to create %s' % name)
					
				(stdout, stderr) = Popen(cmd, stdout=PIPE).communicate()

				'''if subprocess.check_call(cmd, shell=True) == 0:
					if exists(name):
						pass
					else:
						_logger.critical("Container %s was not created" % name)
						self.logSelf("Container %s does not exist" % name)
						return 0
				else:
					return 1'''

			except:
				self.logSelf("Something went wrong creating container %s" % name)   


	def exists(self, name):
		all = self.get_all()
		for container in all:
			if container.name == name:
				return True
		return False


	def get_by_status(self):
		alive, dead, frozen = [], [], []
		cmd = ['lxc-list']
		clist = subprocess.check_output(cmd).splitlines()
		current_list = None
		
		for token in clist:
			token = token.strip()
			if token == "RUNNING":
				current_list = alive
				continue
			if token == "STOPPED":
				current_list = dead
				continue
			if token == "FROZEN":
				current_list = frozen
				continue 
			if len(token) == 0:
				continue
				
			current_list.append(token)
			
		return { 'Running': alive, 'Stopped': dead, 'Frozen': frozen }


	def get_running(self):
		return self.get_by_status()['Running']


	def get_stopped(self):
		return self.get_by_status()['Stopped']


	def get_frozen(self):
		return self.get_by_status()['Frozen']


	def get_all(self):
		all = self.get_by_status()
		running = all['Running']
		frozen = all['Frozen'] 
		stopped = all['Stopped']
		container_list = []
		for container in running:
			conobj = Container()
			conobj.name = container
			conobj.status = 'Running'
			container_list.append(conobj)
		for container in frozen:
			conobj = Container()
			conobj.name = container
			conobj.status = 'Frozen'
			container_list.append(conobj)
		for container in stopped:
			conobj = Container()
			conobj.name = container
			conobj.status = 'Stopped'
			container_list.append(conobj)
		return container_list


	def start(self, name, cfgFile=None):
		self.logSelf('Trying to start %s' % name)
		if self.exists(name):
			try:
				cmd = ['lxc-start', '-n', name, '-d']
				(stdout, stderr) = Popen(cmd, stdout=PIPE).communicate()
			except:
				self.logSelf("Problem starting container: %s" %name)
		else:
			self.logSelf("Container %s does not exist." % name)
			return


	def stop(self, name):
		self.logSelf('Trying to start %s' % name)
		if self.exists(name):
			try:
				cmd = ['lxc-stop', '-n', name]
				(stdout, stderr) = Popen(cmd, stdout=PIPE).communicate()
			except:
				self.logSelf("Problem occurred while stopping container %s" % name)
		else:
			self.logSelf("Container %s does not exist" % name)
			return
		
		
	def restart(self, name, cfgFile=None, cfgValue=None, stateFile=None, stateFd=None):
		if self.exists(name):
			try:
				self.stop(name)
				self.start(name)
			except:     
				self.logSelf("Problem occurred while restarting container %s" % name)
		else:
			self.logSelf("Container %s does not exist" % name)
			return
			
			
	def kill(self, name, killSignal):
		if self.exists(name):
			try:
				cmd = ['lxc-kill', '--name=%s' % name, signal]
				subprocess.check_call(cmd)
			except:
				self.logSelf("Problem occurred while killing container %s" % name)
		else:
			self.logSelf("Container %s does not exist" % name)
			return
	
	
	def destroy(self, name):
		if self.exists(name):
			try:
				cmd = ['lxc-destroy', '-f', '-n', name]
				subprocess.check_call(cmd)
			except:
				self.logSelf("Problem occurred while destroying container %s" % name)
		else:
			self.logSelf("Container %s does not exist" % name)
			return
	
	#not sure if still supported
	def shutdown(self, name, wait=False, reboot=False):
		if self.exists(name):
			try:
				cmd = ['lxc-shutdown', '-n', name]
				if wait:
					cmd.append('-w')
				if reboot:
					cmd.append('-r')
				subprocess.check_call(cmd)
			except:
				self.logSelf("Problem occurred while shutting down container %s" % name)
		else:
			self.logSelf("Container %s does not exist" % name)
			return

	def freeze(self, name):
		if self.exists(name):
			try:
				cmd = ['lxc-freeze', '-n', name]
				subprocess.check_call(cmd)
			except:
				self.logSelf("Problem occurred while freezing container %s" % name)
		else:
			self.logSelf("Container %s does not exist!" % name)
			return


	def unfreeze(self, name):
		if self.exists(name):
			try:
				cmd = ['lxc-unfreeze', '-n', name]
				subprocess.check_call(cmd)
			except:
				self.logSelf("Problem occurred while unfreezing container %s" % name)
		else:
			self.logSelf("Container %s does not exist!" % name)
			return

class Container(object):
	def __init__(self, name=None, status=None):
		self.name = name if name else ''
		self.status = status if status else ''
		
