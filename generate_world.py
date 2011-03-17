from nbt import *
from nbt.mapbuilder import utilities
from nbt.region import RegionFile
from StringIO import StringIO
import argparse, os, random, sys, time

# Set up CLI parameters
parser = argparse.ArgumentParser(description="Generate a Minecraft World")
parser.add_argument('name', metavar='Name', nargs='?', help="Name of the world folder")
parser.add_argument('-d','--directory', default='./', help="Directory the world folder will be created in. Defaults to current directory")
parser.add_argument('-x','--width', type=int, default=2, help="Number of chunks east-west to create")
parser.add_argument('-z','--height', type=int, default=2, help="Number of chunks north-south to create")
args = parser.parse_args()

# Create world folder
if (args.name == None):
	print "No world name supplied!"
	parser.print_help()
	sys.exit()
	
world_folder = args.directory+args.name
if (os.path.exists(world_folder)):
	print "Folder already exists at "+world_folder
	sys.exit()
os.mkdir(world_folder)

# Create a region file
# http://www.minecraftwiki.net/wiki/Beta_Level_Format#Region_Files
os.mkdir(world_folder+"/region")
region_x = 0
region_z = 0
region_filename = world_folder+'/region/r.'+str(region_x)+'.'+str(region_z)+'.mcr'
utilities.blank_region(region_filename)
region = RegionFile(region_filename)
chunk_blocks = {}
chunk_blocks = utilities.draw_disk((7,7,5), 10, chunk_blocks)
for x in range(args.width):
	for z in range(args.height):
		chunk = NBTFile() # Blank NBT
		chunk.name = "Level"
		chunk.tags.extend([
			TAG_Byte(name="TerrainPopulated", value=1),
			TAG_Int(name="xPos", value=x),
			TAG_Int(name="zPos", value=z),
			TAG_Long(name="LastUpdate", value=0),
			TAG_Byte_Array(name="BlockLight", buffer=0),
			TAG_Byte_Array(name="Blocks", buffer=0),
			TAG_Byte_Array(name="Data", buffer=0),
			TAG_Byte_Array(name="SkyLight", buffer=0),
			TAG_Byte_Array(name="HeightMap", buffer=0),
			TAG_List(name="Entities", type=TAG_Compound),
			TAG_List(name="TileEntities", type=TAG_Compound)
		])
		buffer = StringIO()
		chunk.write_file(fileobj=buffer)
		region.write_chunk(x,z, buffer)

# Create a level.dat
# http://www.minecraftwiki.net/wiki/Alpha_Level_Format#level.dat_Format
spawn_x = args.width*8
spawn_z = args.height*8

level = NBTFile() # Blank NBT
level.name = "Data"
level.tags.extend([
	TAG_Long(name="Time", value=1),
	TAG_Long(name="LastPlayed", value=int(time.time())),
	TAG_Int(name="SpawnX", value=spawn_x),
	TAG_Int(name="SpawnY", value=2),
	TAG_Int(name="SpawnZ", value=spawn_z),
	TAG_Long(name="SizeOnDisk", value=0),
	TAG_Long(name="RandomSeed", value=random.randrange(1,9999999999)),
	TAG_Int(name="version", value=19132),
	TAG_String(name="LevelName", value="Testing")
])

player = TAG_Compound()
player.name = "Player"
player.tags.extend([
	TAG_Int(name="Score", value=0),
	TAG_Int(name="Dimension", value=0)
])
inventory = TAG_Compound()
inventory.name = "Inventory"
player.tags.append(inventory)
level.tags.append(player)

level.write_file(world_folder+"/level.dat")
