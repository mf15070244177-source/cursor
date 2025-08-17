from __future__ import annotations

import random
from typing import List, Optional, Set, Tuple

from .models import Indexes, Settings


class BotEngine:
	def __init__(self, indexes: Indexes, settings: Settings):
		self.indexes = indexes
		self.settings = settings

	def _candidates_from(self, prev_word: str, used: Set[str]) -> List[str]:
		last_key = self.indexes.last_key_of[prev_word]
		cands = self.indexes.start_index.get(last_key, [])
		if not self.settings.allow_repeat_idiom:
			cands = [w for w in cands if w not in used]
		return cands

	def _rank_candidates(self, candidates: List[str]) -> List[Tuple[str, int]]:
		return sorted(((w, self.indexes.out_degree.get(w, 0)) for w in candidates), key=lambda x: x[1], reverse=True)

	def pick_next(self, prev_word: str, used: Set[str]) -> Optional[str]:
		cands = self._candidates_from(prev_word, used)
		if not cands:
			return None
		ranked = self._rank_candidates(cands)
		diff = self.settings.difficulty
		if diff == "easy":
			# Prefer lower out-degree to be nicer to player; random among bottom 50%
			half = max(1, len(ranked) // 2)
			pool = [w for w, _ in ranked[-half:]]
			return random.choice(pool)
		elif diff == "hard":
			# Prefer top 10% greedy
			top_k = max(1, len(ranked) // 10)
			pool = [w for w, _ in ranked[:top_k]]
			return random.choice(pool)
		else:
			# normal: bias towards higher out-degree but allow exploration
			top_k = max(1, len(ranked) // 3)
			pool = [w for w, _ in ranked[:top_k]]
			if random.random() < 0.25:
				pool = [w for w, _ in ranked]
			return random.choice(pool)

	def suggest(self, prev_word: str, used: Set[str], limit: int = 5) -> List[str]:
		cands = self._candidates_from(prev_word, used)
		ranked = self._rank_candidates(cands)
		return [w for w, _ in ranked[:limit]]