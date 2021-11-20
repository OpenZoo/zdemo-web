#!/usr/bin/env python3

from dataclasses import dataclass
from struct import unpack
import io, os

@dataclass
class ZzdCommand:
	id: int
	position: int

@dataclass
class ZzdCommandInput(ZzdCommand):
	count: int
	delta_x: int
	delta_y: int
	flags: int
	key_pressed: int

	def __post_init__(self):
		self.shift_pressed = (self.flags & 0x01) != 0

@dataclass
class ZzdCommandReseed(ZzdCommand):
	random_seed: int

@dataclass
class ZzdCommandGameStart(ZzdCommand):
	random_seed: int
	tick_speed: int

@dataclass
class ZzdCommandGameStop(ZzdCommand):
	pass

@dataclass
class ZzdCommandPitTickDelta(ZzdCommand):
	tick_delta: int
		
@dataclass
class ZzDemoData:
	magic: int
	version: int
	name: str
	engine_name: str
	flags: int
	commands: list[ZzdCommand]

	def __init__(self, data: bytes):
		with io.BytesIO(data) as f:
			self.magic, self.version = unpack('<HH', f.read(4))
			entry_pos = 0

			self.name = ''
			self.engine_name = ''
			self.flags = 0

			if self.magic != 0xD327:
				raise Exception("Invalid magic!")
			elif self.version == 0x0001:
				self.name, self.flags = unpack('<21pB', f.read(22))
				self.name = self.name.decode('cp437')
			elif self.version == 0x0002:
				self.name, self.flags, self.engine_name = unpack('<21pB31p', f.read(53))
				self.name = self.name.decode('cp437')
				self.engine_name = self.engine_name.decode('cp437')
			else:
				raise Exception("Invalid version!")

			self.commands = []

			f_data_start = f.tell()
			f.seek(0, os.SEEK_END)
			f_end = f.tell()
			f.seek(f_data_start)
			while f.tell() != f_end:
				f_pos = f.tell()
				cmd_type = unpack('<B', f.read(1))[0]
				if cmd_type == 0:
					count, delta_x, delta_y, flags, key_pressed = unpack('<hbbBB', f.read(6))
					cmd = ZzdCommandInput(cmd_type, entry_pos, count, delta_x, delta_y, flags, key_pressed)
				elif cmd_type == 1:
					random_seed = unpack('<I', f.read(4))[0]
					cmd = ZzdCommandReseed(cmd_type, entry_pos, random_seed)
				elif cmd_type == 2:
					random_seed, tick_speed = unpack('<Ih', f.read(6))
					cmd = ZzdCommandGameStart(cmd_type, entry_pos, random_seed, tick_speed)
				elif cmd_type == 3:
					cmd = ZzdCommandGameStop(cmd_type, entry_pos)
				elif cmd_type == 4:
					tick_delta = unpack('<h', f.read(2))[0]
					cmd = ZzdCommandPitTickDelta(cmd_type, entry_pos, tick_delta)
				else:
					raise Exception(f"Unknown command type: {cmd_type} at {entry_pos}:{f_pos}")
				self.commands.append(cmd)
				entry_pos += 1
				
