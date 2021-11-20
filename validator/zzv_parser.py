#!/usr/bin/env python3

from dataclasses import dataclass
from struct import unpack
import io, os

@dataclass
class ZzValidationData:
	result_message: str
	success: bool
	run_time: int
	recording_time: int
	score: int
	seed: int
	tick_speed: int

	def __init__(self, data: io.TextIOBase):
		self.result_message = data.readline().strip()
		self.success = self.result_message == "Success"

		for line in data.readlines():
			line_split = line.strip().split(":", maxsplit=1)
			if len(line_split) == 2:
				key = line_split[0].strip()
				value = line_split[1].strip()
				if key == "Run time":
					self.run_time = int(value.split("(", maxsplit=1)[1].split(" ", maxsplit=1)[0])
				elif key == "Recording time":
					self.recording_time = int(value.split("(", maxsplit=1)[1].split(" ", maxsplit=1)[0])
				elif key == "Score":
					self.score = int(value)
				elif key == "Seed":
					self.seed = int(value)
				elif key == "Tick speed":
					self.tick_speed = int(value)
			else:
				continue