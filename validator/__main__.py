import asyncio
import os
from demo_player import play_demo
from demo_qualifier import qualify_demo
from world_definitions import gather_world_definitions

if __name__ == "__main__":
	defs = gather_world_definitions()
	with open("../HELLFURY.ZZD", "rb") as f:
		zzd_data = f.read()
	loop = asyncio.get_event_loop()
	result = loop.run_until_complete(qualify_demo("HELLFURY", defs["HELLFURY"], "zdemo_beta1", zzd_data))
	print(result)