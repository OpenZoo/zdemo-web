# Some notes:
# - scorers always sort from largest to smallest ("best run")

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from demo_player import DemoPlaybackResult
from typing import Tuple
import importlib
import os
import sys

def validator_none(result: DemoPlaybackResult) -> bool:
	return True

def scorer_any_percent(result: DemoPlaybackResult) -> Tuple[int, ...]:
	return (-result.run_time, )

def scorer_low_percent(result: DemoPlaybackResult) -> Tuple[int, ...]:
	return (-result.score, -result.run_time)

@dataclass
class WorldCategory:
	category_id: str
	name: str
	validator: Callable[[DemoPlaybackResult], bool] = validator_none
	parent = None

	def __str__(self):
		if self.parent is None:
			return self.name
		else:
			return self.parent.__str__() + " -> " + self.name

	def full_category_id(self):
		if self.parent is None:
			return self.category_id
		else:
			return self.parent.full_category_id() + ":" + self.category_id

@dataclass
class WorldCategoryLeaf(WorldCategory):
	scorer: Callable[[DemoPlaybackResult], Tuple[int, ...]] = scorer_any_percent

@dataclass
class WorldCategoryNode(WorldCategory):
	children: list[WorldCategory] = field(default_factory = list)

	def __post_init__(self):
		for c in self.children:
			c.parent = self

@dataclass
class WorldDefinition:
	name: str
	world_name: str
	categories: list[WorldCategory] = field(default_factory = list)
	validator: Callable[[DemoPlaybackResult], bool] = validator_none

	def __post_init__(self):
		def validate_categories(categories: Iterable[WorldCategory]):
			for c in categories:
				if isinstance(c, WorldCategoryNode):
					if len(c.children) <= 0:
						raise Exception("World category node without children: " + c.full_category_id())
					validate_categories(c.children)
		validate_categories(self.categories)

	def qualify_run(self, result: DemoPlaybackResult) -> list[Tuple[WorldCategoryLeaf, Tuple[int, ...]]]:		
		scores = list()
		def add_leaves(categories: Iterable[WorldCategory]):
			for c in categories:
				if not c.validator(result):
					continue
				if isinstance(c, WorldCategoryNode):
					add_leaves(c.children)
				elif isinstance(c, WorldCategoryLeaf):
					scores.append((c, c.scorer(result)))
		add_leaves(self.categories)
		return scores

def gather_world_definitions() -> dict[str, WorldDefinition]:
	result = dict()
	for dir_name in os.listdir("../worlds"):
		dir_path = f"../worlds/{dir_name}"
		if os.path.isdir(dir_path):
			def_path = f"{dir_path}/main.py"
			if os.path.exists(def_path):
				module_name = f".worlds.{dir_name}.main"
				spec = importlib.util.spec_from_file_location(module_name, def_path)
				module = importlib.util.module_from_spec(spec)
				sys.modules[module_name] = module
				spec.loader.exec_module(module)	
				result[dir_name] = module.definition
	return result