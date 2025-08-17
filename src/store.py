from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from pydantic import ValidationError

from .models import Idiom, Settings, Indexes, UserState
from .utils import normalize_text, first_key as get_first_key, last_key as get_last_key, char_key


def load_config(config_path: Path) -> Dict:
	if not config_path.exists():
		return {}
	try:
		with config_path.open("r", encoding="utf-8") as f:
			return json.load(f)
	except json.JSONDecodeError:
		return {}


def merge_config(base: Dict, overrides: Dict) -> Settings:
	merged = dict(base)
	for k, v in overrides.items():
		merged[k] = v
	try:
		return Settings(**merged)
	except ValidationError as e:
		raise RuntimeError(f"Invalid configuration: {e}")


def load_idioms(path: str) -> List[Idiom]:
	file_path = Path(path)
	if not file_path.exists():
		raise FileNotFoundError(f"Dictionary file not found: {path}")
	with file_path.open("r", encoding="utf-8") as f:
		data = json.load(f)
	idioms: List[Idiom] = []
	for item in data:
		if isinstance(item, str):
			word = normalize_text(item)
			idioms.append(Idiom(word=word))
		elif isinstance(item, dict) and "word" in item:
			word = normalize_text(item["word"]) 
			pinyin = item.get("pinyin")
			idioms.append(Idiom(word=word, pinyin=pinyin))
		else:
			continue
	# de-duplicate by word while preserving order
	seen = set()
	unique: List[Idiom] = []
	for it in idioms:
		if it.word not in seen:
			unique.append(it)
			seen.add(it.word)
	return unique


def build_indexes(idioms: List[Idiom], mode: str, strict_pinyin: bool) -> Indexes:
	start_index: Dict[str, List[str]] = {}
	last_key_of: Dict[str, str] = {}
	first_key_of: Dict[str, str] = {}

	for it in idioms:
		w = it.word
		fk = get_first_key(w, mode, strict_pinyin)
		lk = get_last_key(w, mode, strict_pinyin)
		first_key_of[w] = fk
		last_key_of[w] = lk
		start_index.setdefault(fk, []).append(w)

	# compute out-degree: number of possible next idioms for each idiom
	out_degree: Dict[str, int] = {}
	for it in idioms:
		w = it.word
		lk = last_key_of[w]
		candidates = start_index.get(lk, [])
		out_degree[w] = len(candidates)

	return Indexes(start_index=start_index, out_degree=out_degree, last_key_of=last_key_of, first_key_of=first_key_of)


def load_user_state(path: str) -> UserState:
	file_path = Path(path)
	if not file_path.exists():
		return UserState()
	try:
		with file_path.open("r", encoding="utf-8") as f:
			data = json.load(f)
		return UserState(**data)
	except Exception:
		return UserState()


def save_user_state(path: str, state: UserState) -> None:
	file_path = Path(path)
	file_path.parent.mkdir(parents=True, exist_ok=True)
	with file_path.open("w", encoding="utf-8") as f:
		json.dump(state.model_dump(), f, ensure_ascii=False, indent=2)