#!/usr/bin/env python3

from dataclasses import dataclass
from struct import unpack
import io, os

@dataclass
class ZzLogSplit:
	pit_ticks: int
	split_type: str
	board_id: int
	board_name: str

	def __str__(self):
		return f"[{self.pit_ticks}] {self.split_type}: {self.board_name} ({self.board_id})"

@dataclass
class ZzLogData:
	splits: list[ZzLogSplit]
	complete: bool

	def __init__(self, data: io.TextIOBase):
		self.splits = []
		found_start = False
		found_stop = False
		pit_tick_offset = -1
		for line in data.readlines():
			line_split = line.split(" ", maxsplit=3)
			if len(line_split) < 3:
				continue

			pit_ticks = int(line_split[0])
			split_type = line_split[1]
			board_id = int(line_split[2])
			board_name = line_split[3] if len(line_split) >= 4 else ''

			if split_type not in ["START", "SPLIT", "STOP"]:
				continue
			found_start = found_start or (split_type == "START")
			found_stop = found_stop or (split_type == "STOP")
			if pit_tick_offset is None:
				if line_split[1] != "START":
					raise Exception("ZZL file does not begin with START command!")
				pit_tick_offset = pit_ticks			
			self.splits.append(ZzLogSplit(pit_ticks - pit_tick_offset, split_type, board_id, board_name))
		self.complete = found_start and found_stop
