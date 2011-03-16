class block_recipe:
	def __init__(self):
		self.blocks = {} # empty dictionary
		self.max_x = None
		self.max_y = None
		self.max_z = None
		self.min_x = None
		self.min_y = None
		self.min_z = None
	
	def add_block(self, coord, block_id):
		if (len(coord) != 3):
			raise Exception('Not a valid coordinate')
		
		self.blocks[coord] = block_id # Save the block assignment
		
		# Update extents
		if (self.min_x == None or coord[0] < self.min_x):
			self.min_x = coord[0]
		if (self.max_x == None or coord[0] > self.max_x):
			self.max_x = coord[0]
		if (self.min_y == None or coord[1] < self.min_y):
			self.min_y = coord[1]
		if (self.max_y == None or coord[1] > self.max_y):
			self.max_y = coord[1]
		if (self.min_z == None or coord[2] < self.min_z):
			self.min_z = coord[2]
		if (self.max_z == None or coord[2] > self.max_z):
			self.max_z = coord[2]
	
	def get_extents(self):
		min = self.min_x, self.min_y, self.min_z
		max = self.max_x, self.max_y, self.max_z
		return min,max
	
	def get_volume(self):
		min,max = self.get_extents()
		delta_x = abs(max[0]-min[0])+1
		delta_y = abs(max[1]-min[1])+1
		delta_z = abs(max[2]-min[2])+1
		print str(delta_x)+","+str(delta_y)+","+str(delta_z)
		return delta_x*delta_y*delta_z
		
