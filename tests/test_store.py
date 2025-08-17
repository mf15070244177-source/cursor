import json
from pathlib import Path

from src.store import build_indexes, save_user_state, load_user_state
from src.models import Idiom, Settings


def test_build_indexes_basic(tmp_path: Path):
	idioms = [
		Idiom(word="一鸣惊人"),
		Idiom(word="人山人海"),
		Idiom(word="海阔天空"),
		Idiom(word="空前绝后"),
	]
	idx = build_indexes(idioms, mode="char", strict_pinyin=False)
	# start_index should have entries for first chars
	assert "一" in idx.start_index
	assert "人" in idx.start_index
	# out degree of "一鸣惊人" should be number of idioms starting with "人"
	assert idx.out_degree["一鸣惊人"] == len(idx.start_index.get("人", []))


def test_user_state_persistence(tmp_path: Path):
	file = tmp_path / "user_state.json"
	state = load_user_state(str(file))
	assert state.high_score == 0
	state.high_score = 100
	save_user_state(str(file), state)
	loaded = load_user_state(str(file))
	assert loaded.high_score == 100