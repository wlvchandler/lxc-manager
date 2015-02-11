import lxc

from ajenti.api import plugin
from ajenti.plugins.main.api import SectionPlugin
from ajenti.ui import on
from ajenti.ui.binder import Binder


def get(value):
	return value() if callable(value) else value
	
class Instance(object):
	def __init__(self, name=None, template=None, parameters=None):
		self.name = name if name else '{Empty}'
		self.template = status if template else '{Empty}'
		self.parameters = parameters if parameters else '{Empty}'

class confirmDialog(object):
	def __init__(self):
		self.message = ''

@plugin
class Test (SectionPlugin):
	def init(self):
		self.title = 'Instance Manager'
		self.icon = 'th-list'
		self.category = 'System'
		self.mgr = lxc.lxcman()

		#change 'dialogging:..' to match the name of directory
		self.append(self.ui.inflate('dialogging:main'))
		
		def post_item_bind(object, collection, item, ui):
			ui.find('btnStart').on('click', self.on_start, item)
			ui.find('btnRestart').on('click', self.on_restart, item)
			ui.find('btnStop').on('click', self.on_stop, item)
			ui.find('btnRemove').on('click', self.on_remove, item)
			#ui.find('btnSnapshot').on('click', self.on_snapshot, item)
			
			running = True if item.name in self.mgr.get_running() else False
			frozen = True if item.name in self.mgr.get_frozen() else False
			
			ui.find('btnStart').visible = not running
			ui.find('btnRestart').visible = running
			ui.find('btnStop').visible = running
			ui.find('btnFreeze').visible = not frozen
			ui.find('btnUnfreeze').visible = frozen

		self.find('collection').post_item_bind = post_item_bind

		self.obj_collection = self.mgr.get_all()

		self.binder = Binder(self, self)
		self.find('btnSnapshot').visible = False
		self.refresh()

	def refresh(self):
		self.populate()
		self.binder.update()
	
	def populate(self):
		self.obj_collection = self.mgr.get_all()
		for i in self.obj_collection:
			i._status = get(i.status)
			i._name = i.name
		self.binder.setup(self).populate()

	@on('btnCreateDialog', 'click')
	def on_apply(self):
		self.find('dialog').visible = True
		self.created = Instance()
		self.binder_d = Binder(self.created, self.find('dialog')).populate()
	
	@on('dialog', 'button')
	def on_close_dialog(self, button):
		self.find('dialog').visible = False
		if button == 'save':
			self.binder_d.update()
			self.created.name = self.created.name.replace(' ', '-')
			self.mgr.create(self.created.name)
		if self.mgr.exists(self.created.name):
			self.context.notify('info', "%s created" % self.created.name)
		self.refresh()

	def on_start(self, container):
		self.mgr.start(container.name.strip())
		self.populate()
		running = self.mgr.get_running()
		if container.name in running:
			self.context.notify('info', "%s started successfully" % container.name)
		self.refresh()
		
	def on_stop(self, container):
		self.mgr.stop(container.name.strip())
		self.populate()
		stopped = self.mgr.get_stopped()
		if container.name in stopped:
			self.context.notify('info', "%s stopped successfully" % container.name)
		self.refresh()
		
	def on_restart(self, container):
		self.mgr.restart(container.name.strip())
		self.populate()
		running = self.mgr.get_running()
		if container.name in running:
			self.context.notify('info', "%s restarted successfully" % container.name)
		self.refresh()
		
	def on_remove(self, container):
		self.find('confirmDialog').visible=True
		self.conf = confirmDialog()
		self.conf.name = container.name.strip()
		self.conf.message = 'Really delete %s ?' % self.conf.name
		self.binder_r = Binder(self.conf , self.find('confirmDialog')).populate()
	
	@on('confirmDialog','button')
	def on_remove_close(self, button):
		self.find('confirmDialog').visible=False
		if button == 'confirm':
			self.mgr.destroy(self.conf.name)
			self.populate()
			running = self.mgr.get_running()
			if self.conf.name not in running:
				self.context.notify('info', "%s removed successfully" % self.conf.name)
		self.refresh()
		
'''	def on_snapshot(self, container):
		self.find('snapDialog').visible=True
		#self.binder_s = Binder()
		#self.mgr.snapshot(container.name.strip())
		self.populate()
		running = self.mgr.get_running()
		if container.name not in running:
			self.context.notify('info', "%s removed successfully" % container.name)
		self.refresh()
	
	@on('snapDialog', 'button')
	def on_snap_close(self, button):
		self.find('snapDialog').visible=False'''
