from ajenti.api import *
from ajenti.plugins import *

info = PluginInfo(
	title='Instance Manager',
	icon='th-list',
	dependencies=[
		PluginDependency('main'),
	],
)

def init():
	import main
