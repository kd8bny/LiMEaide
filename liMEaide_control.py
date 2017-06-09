import threading

class MasterControl(threading.Thread):
	'''define job parameters'''
	def __init__(self, group=None, target=None, name=None,
		args=(), kwargs=None, daemon=True):
		threading.Thread.__init__(self, group=None, target=target, name=name, daemon=daemon)
		self.args = args
		self.kwargs = args
		self.name = name
		self.target = target
		self.daemon = daemon
