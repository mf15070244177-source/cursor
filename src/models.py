from __future__ import annotations

from typing import Dict, List, Optional, Set, Literal
from pydantic import BaseModel, Field


GameMode = Literal["char", "pinyin"]
Difficulty = Literal["easy", "normal", "hard"]


class Idiom(BaseModel):
	word: str
	pinyin: Optional[str] = None

	class Config:
		frozen = True


class Settings(BaseModel):
	mode: GameMode = "char"
	strict_pinyin: bool = False
	timer_seconds: int = 20
	difficulty: Difficulty = "normal"
	allow_repeat_idiom: bool = False
	dictionary_path: str = "data/idioms.json"
	max_hints: int = 5
	save_path: str = "data/user_state.json"


class Indexes(BaseModel):
	# Mapping from start key -> list of idiom words starting with that key
	start_index: Dict[str, List[str]] = Field(default_factory=dict)
	# Mapping from idiom word -> its out-degree in the graph
	out_degree: Dict[str, int] = Field(default_factory=dict)
	# Mapping from idiom word -> last key
	last_key_of: Dict[str, str] = Field(default_factory=dict)
	# Mapping from idiom word -> first key
	first_key_of: Dict[str, str] = Field(default_factory=dict)


class GameState(BaseModel):
	used_idioms: Set[str] = Field(default_factory=set)
	current_score: int = 0
	streak_count: int = 0
	last_player_word: Optional[str] = None
	last_bot_word: Optional[str] = None
	hints_used: int = 0


class UserState(BaseModel):
	high_score: int = 0
	games_played: int = 0
	last_settings: Optional[Settings] = None