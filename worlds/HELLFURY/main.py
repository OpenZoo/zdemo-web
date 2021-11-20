from collections.abc import Callable
from ...demo_player import DemoPlaybackResult
from ...world_definitions import *

required_boards = [1, 2]
ending_boards = [6, 7, 8]
board_normal = 3
board_hard = 4
board_evil = 5

def create_validator(main_board: int, won_flag: str):
	def validator(result: DemoPlaybackResult) -> bool:
		return result.is_endgame() \
			and result.has_visited_boards(required_boards) \
			and result.has_visited_board(main_board) \
			and result.is_on_any_board(ending_boards) \
			and result.is_flag_set(won_flag)
	return validator

definition = WorldDefinition("Hell's Fury", "HELLFURY",
	categories = [
		WorldCategoryNode("any_percent", "Any%", children = [
			WorldCategoryLeaf("normal", "Normal", validator = create_validator(board_normal, "won_n")),
			WorldCategoryLeaf("hard", "Hard", validator = create_validator(board_hard, "won_h")),
			WorldCategoryLeaf("evil", "Evil", validator = create_validator(board_evil, "won_e"))
		])
	]
)
