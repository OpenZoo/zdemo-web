from collections.abc import Iterable
from dataclasses import dataclass
from zzd_parser import ZzdCommand, ZzDemoData
from zzl_parser import ZzLogSplit, ZzLogData
from zzv_parser import ZzValidationData
import asyncio
import os
import shutil
import tempfile
import zookeeper

engine_validator_executables = {"ZDEMOVAL.EXE": "ZZT", "SDEMOVAL.EXE": "Super ZZT"}
engine_extensions = {"ZZT": "ZZT", "Super ZZT": "SZT"}

@dataclass
class DemoPlaybackResult:
	commands: list[ZzdCommand]
	splits: list[ZzLogSplit]
	boards_visited: set[int]
	complete: bool
	run_time: int
	recording_time: int
	score: int
	seed: int
	tick_speed: int
	start_world: zookeeper.World
	finish_world: zookeeper.World
	engine: str

	def __init__(self, demo_data: ZzDemoData, log_data: ZzLogData, validation_results: ZzValidationData,
				 sav_data: zookeeper.World, world_data: zookeeper.World):
		self.commands = demo_data.commands
		self.splits = log_data.splits
		self.boards_visited = set(map(lambda x: x.board_id, self.splits))
		self.complete = log_data.complete and validation_results.success
		self.run_time = validation_results.run_time
		self.recording_time = validation_results.recording_time
		self.score = validation_results.score
		self.seed = validation_results.seed
		self.tick_speed = validation_results.tick_speed
		self.start_world = world_data
		self.finish_world = sav_data
		self.engine = world_data.engine
	
	def is_endgame(self):
		return self.finish_world.health <= 0

	def has_visited_board(self, board_id: int):
		return board_id in self.boards_visited

	def has_visited_boards(self, board_ids: Iterable[int]):
		return all(self.has_visited_board(b) for b in board_ids)

	def has_visited_any_board(self, board_ids: Iterable[int]):
		return any(self.has_visited_board(b) for b in board_ids)

	def is_on_board(self, board_id: int):
		return self.finish_world.current_board == board_id

	def is_on_any_board(self, board_ids: Iterable[int]):
		return self.finish_world.current_board in board_ids

	def is_flag_set(self, flag: str):
		for world_flag in self.finish_world.flags:
			if world_flag.name.lower() == flag.lower():
				return True
		return False

	def is_flag_clear(self, flag: str):
		return not is_flag_set(flag)

async def play_demo(world_dir_name: str, world_name: str, engine_name: str, zzd_bytes: bytes) -> DemoPlaybackResult:
	with tempfile.TemporaryDirectory() as temp_dir:
		# Prepare directory
		world_dir = f"../worlds/{world_dir_name}"
		for file_name in os.listdir(world_dir):
			shutil.copy(f"{world_dir}/{file_name}", f"{temp_dir}/{file_name}")
		engine_dir = f"../engines/{engine_name}"
		validator_exe = None
		for file_name in os.listdir(engine_dir):
			if file_name in engine_validator_executables.keys():
				validator_exe = file_name
			shutil.copy(f"{engine_dir}/{file_name}", f"{temp_dir}/{file_name}")
		if validator_exe is None:
			raise Exception("Could not find validator .EXE!")
		with open(f"{temp_dir}/{world_name}.ZZD", "wb") as f:
			f.write(zzd_bytes)
		# Parse early information (as to not bog down Zeta if something crashes here)
		engine = engine_validator_executables[validator_exe]
		world_ext = engine_extensions[engine]
		world_data = zookeeper.Zookeeper(f"{temp_dir}/{world_name}.{world_ext}")
		demo_data = ZzDemoData(zzd_bytes)
		# Run Zeta
		proc = await asyncio.create_subprocess_exec(
			os.path.abspath(f"../tools/zeta86"), "-e", f"{validator_exe} {world_name}",
			stdin=asyncio.subprocess.PIPE,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
			cwd=f"{temp_dir}/"
		)
		proc_out, proc_err = await proc.communicate()
		if (not os.path.isfile(f"{temp_dir}/{world_name}.ZZL")) \
		or (not os.path.isfile(f"{temp_dir}/RESULT.ZZV")) \
		or (not os.path.isfile(f"{temp_dir}/RESULT.SAV")):
			raise Exception("Insufficient output data!")
		with open(f"{temp_dir}/{world_name}.ZZL", "r", encoding="cp437") as f:
			log_data = ZzLogData(f)
		with open(f"{temp_dir}/RESULT.ZZV", "r", encoding="cp437") as f:
			validation_results = ZzValidationData(f)
		sav_data = zookeeper.Zookeeper(f"{temp_dir}/RESULT.SAV")
		return DemoPlaybackResult(demo_data, log_data, validation_results, sav_data.world, world_data.world)
