from dataclasses import dataclass
from demo_player import DemoPlaybackResult, play_demo
from typing import Tuple
from world_definitions import WorldDefinition
import asyncio

@dataclass
class DemoQualificationResult:
	playback_result: DemoPlaybackResult
	scoring: dict[str, Tuple[int, ...]]

async def qualify_demo(world_definition_key: str, world_definition: WorldDefinition, engine_name: str, zzd_bytes: bytes):
	result = await play_demo(world_definition_key, world_definition.world_name, engine_name, zzd_bytes)
	score_list = world_definition.qualify_run(result)
	score_map = dict()
	for l in score_list:
		score_map[l[0].full_category_id()] = l[1]
	return DemoQualificationResult(result, score_map)