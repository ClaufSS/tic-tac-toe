from time import time

# Temporary Time Markers
class TTCMarkers:
	def __getitem__(self, marker):
		return self.__dict__.pop(marker, None)
		
	def __setitem__(self, marker, value):
		if marker not in self.__dict__:
			setattr(self, marker, value)
			
	def __delitem__(self, marker):
		if hasattr(self, marker):
			delattr(self, marker)
			
# Persistent Time Markers
class TCMarkers:
	def __getitem__(self, marker):
		return getattr(self, marker, None)
		
	def __setitem__(self, marker, value):
		if not hasattr(self, marker):
			setattr(self, marker, value)
			
	def __delitem__(self, marker):
		delattr(self, marker)

# Core of the Time Counters
class TC:
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.__markers = TCMarkers()
		self.__tmarkers = TTCMarkers()
	
	def set_timeMarker(self, marker='', persistent=False, offset=0):
		if marker == '':
			raise Exception('Set a empty marker name')
		
		if persistent:
			self.__markers[marker] = time() + offset
		else:
			self.__tmarkers[marker] = time() + offset
			
		return offset
	
	def get_timeMarker(self, marker='', *args):
		tmk = self.__tmarkers[marker]
		if tmk != None:
			return self.time_transform(time() - tmk)
		
		mk = self.__markers[marker]
		if mk != None:
			return time() - mk
		
		raise Exception('Inexistent marker')
	
	def destroy(self, marker=''):
		if marker == '':
			raise Exception('Set a valid marker name')
			
		if hasattr(self.__markers, marker):
			del(self.__markers[marker])
			return
			
		if hasattr(self.__tmarkers, marker):
			del(self.__tmarkers[marker])
			return
			
		raise Exception('Inexistent marker')
	
	def time_transform(self, time):
		mnt, scnd = [f'{i}'.rjust(2, '0') for i in divmod(int(time), 60)]
		return f'{mnt}:{scnd}'
		