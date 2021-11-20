from ...demo_player import DemoPlaybackResult
from ...world_definitions import *

def validate_normal(result: DemoPlaybackResult) -> bool:
	return result.is_endgame() \
		and result.has_visited_board(1) \
		and result.is_on_board(31)

definition = WorldDefinition("When East Met West: The Pact of Steel", "ATOMIC",
	categories = [
		WorldCategoryLeaf("any_percent", "Any%", validator = validate_normal)
	]
)
