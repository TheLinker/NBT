""" Handle a single chunk of data (16x16x128 blocks) """
from StringIO import StringIO
from struct import pack, unpack
import array

class Chunk(object):
	def __init__(self, x, z, length):
		self.coords = x,z
		self.length = length
	
	def __repr__(self):
		return "("+str(self.coords[0])+","+str(self.coords[1])+"): "+str(self.length)

""" Convenience class for dealing with a Block/data byte array """
class BlockArray(object):
	def __init__(self, blocksBytes=None, dataBytes=None):
		if (blocksBytes != None):
			self.blocksList = [ord(b) for b in blocksBytes] # A list of bytes
		else:
			# Create an empty block list (32768 entries of zero (air))
			self.blocksList = []
			for i in range(4096):
				self.blocksList.extend([0,0,0,0,0,0,0,0])
		
		if (dataBytes != None):
			self.dataList = [ord(b) for b in dataBytes]
		else:
			# Create an empty data list (32768 entries of zero)
			self.dataList = []
			for i in range(4096):
				self.dataList.extend([0,0,0,0,0,0,0,0])
			

	# Get all data entries
	def get_all_data(self):
		bits = []
		for b in self.dataList:
			bits.append((b >> 15) & 15) # Big end of the byte
			bits.append(b & 15) # Little end of the byte
		return bits
	
	def get_blocks_struct(self):
		cur_x = 0
		cur_y = 0
		cur_z = 0
		blocks = {}
		for block_id in self.blocksList:
			blocks[(cur_x,cur_y,cur_z)] = block_id
			cur_y += 1
			if (cur_y > 127):
				cur_y = 0
				cur_z += 1
				if (cur_z > 15):
					cur_z = 0
					cur_x += 1
		return blocks
	
	# Give blockList back as a byte array
	def get_blocks_byte_array(self, buffer=False):
		if buffer:
			length = len(self.blocksList)
			return StringIO(pack(">i", length)+self.get_blocks_byte_array())
		else:
			return array.array('B', self.blocksList).tostring()
		
	def get_data_byte_array(self, buffer=False):
		if buffer:
			length = len(self.dataList)/2
			return StringIO(pack(">i", length)+self.get_data_byte_array())
		else:
			return array.array('B', self.dataList).tostring()
	
	def get_heightmap(self, buffer=False):
		if buffer:
			return StringIO(pack(">i", 256)+self.get_heightmap())
		else:
			bytes = []
			for z in range(16):
				for x in range(16):
					for y in range(127, -1, -1):
						offset = y + z*128 + x*128*16
						if (self.blocksList[offset] != 0 or y == 0):
							bytes.append(y)
							break
			return array.array('B', bytes).tostring()
						
						
	def set_blocks(self, list=None, dict=None, fill_air=False):
		if list:
			# Inputting a list like self.blocksList
			self.blocksList = list
		elif dict:
			# Inputting a dictionary like result of self.get_blocks_struct()
			list = []
			for x in range(16):
				for z in range(16):
					for y in range(128):
						coord = x,y,z
						offset = y + z*128 + x*128*16
						if (coord in dict):
							list.append(dict[coord])
						else:
							if (self.blocksList[offset] and not fill_air):
								list.append(self.blocksList[offset])
							else:
								list.append(0) # Air
			self.blocksList = list
		else:
			# None of the above...
			return False
		return True
	
	def set_block(self, x,y,z, id):
		offset = y + z*128 + x*128*16
		self.blocksList[offset] = id

	
	# Get a given X,Y,Z
	def get_block(self, x,y,z):
		"""
		Laid out like:
		(0,0,0), (0,1,0), (0,2,0) ... (0,127,0), (0,0,1), (0,1,1), (0,2,1) ... (0,127,1), (0,0,2) ... (0,127,15), (1,0,0), (1,1,0) ... (15,127,15)
		
		blocks = []
		for x in xrange(15):
		  for z in xrange(15):
		    for y in xrange(127):
		      blocks.append(Block(x,y,z))
		"""
		
		offset = y + z*128 + x*128*16
		return self.blocksList[offset]

	# Get a given X,Y,Z
	def get_data(self, x,y,z):
		offset = y + z*128 + x*128*16
		#print "Offset: "+str(offset)
		if (offset % 2 == 1):
			# offset is odd
			index = (offset-1)/2
			b = self.dataList[index]
			#print "Byte: %02X" % b
			return (b >>15) & 15 # Get big end of byte
		else:
			# offset is even
			index = offset/2
			b = self.dataList[index]
			#print "Byte: %02X" % b
			return b & 15