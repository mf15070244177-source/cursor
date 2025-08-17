from __future__ import annotations

import time
from typing import List, Optional, Set

from .models import Settings, Indexes, Idiom, GameState, UserState
from .rules import ensure_valid_user_input, check_in_dictionary, ensure_chain, ensure_not_repeated, ValidationErrorInfo
from .engine import BotEngine
from .io_cli import render_header, render_status, render_turn_info, render_error, render_hint_list, render_game_over, render_help, read_user_input_with_timeout, render_info


class IdiomGame:
	def __init__(self, settings: Settings, indexes: Indexes, idioms: List[Idiom], user_state: UserState):
		self.settings = settings
		self.indexes = indexes
		self.idioms = idioms
		self.user_state = user_state
		self.state = GameState()
		self.bot = BotEngine(indexes=indexes, settings=settings)
		self.dictionary_words: Set[str] = {it.word for it in idioms}
		self.history: List[str] = []  # for undo: store only player's last move

	def _score_for_valid_move(self) -> int:
		base = 10
		bonus = self.state.streak_count * 2
		return base + bonus

	def _apply_score(self):
		points = self._score_for_valid_move()
		self.state.current_score += points
		self.state.streak_count += 1

	def _reset_streak(self):
		self.state.streak_count = 0

	def _handle_player_move(self, raw_input: str) -> Optional[str]:
		word = ensure_valid_user_input(raw_input)
		check_in_dictionary(word, self.dictionary_words)
		ensure_not_repeated(word, self.state.used_idioms, self.settings.allow_repeat_idiom)
		if self.history:
			prev = self.history[-1]
			ensure_chain(prev, word, self.settings)
		self.state.used_idioms.add(word)
		self.history.append(word)
		self.state.last_player_word = word
		self._apply_score()
		return word

	def _bot_move(self, prev_word: str) -> Optional[str]:
		next_word = self.bot.pick_next(prev_word, self.state.used_idioms)
		if next_word is None:
			return None
		self.state.used_idioms.add(next_word)
		self.state.last_bot_word = next_word
		return next_word

	def _handle_command(self, cmd: str) -> Optional[str]:
		cmd = cmd.strip().lower()
		if cmd == ":help":
			render_help()
			return None
		if cmd == ":quit":
			raise SystemExit
		if cmd == ":hint":
			if self.state.hints_used >= self.settings.max_hints:
				render_error("没有剩余提示")
				return None
			if not self.history:
				render_error("还没有开始，无法提示")
				return None
			prev = self.history[-1]
			hints = self.bot.suggest(prev, self.state.used_idioms, limit=5)
			render_hint_list(hints)
			self.state.hints_used += 1
			return None
		if cmd == ":undo":
			if not self.history:
				render_error("没有可悔步的记录")
				return None
			last = self.history.pop()
			if last in self.state.used_idioms:
				self.state.used_idioms.remove(last)
			self.state.last_player_word = None
			self._reset_streak()
			render_info("已悔步：撤销你的上一步")
			return None
		return None

	def run(self) -> None:
		render_header()
		round_index = 0
		while True:
			# Show status
			render_status(self.state.current_score, self.state.streak_count, self.settings.max_hints - self.state.hints_used, self.settings.mode, self.settings.difficulty)
			render_turn_info(self.state.last_player_word, self.state.last_bot_word)

			prompt = f"[{self.settings.timer_seconds}s] 请输入四字成语（或 :help）："
			res = read_user_input_with_timeout(prompt, self.settings.timer_seconds)
			if res.timeout:
				reason = "超时"
				self._end_game(reason)
				return
			user_input = res.user_input or ""
			if user_input.startswith(":"):
				try:
					self._handle_command(user_input)
					continue
				except SystemExit:
					self._end_game("主动退出")
					return

			try:
				player_word = self._handle_player_move(user_input)
			except ValidationErrorInfo as e:
				self._end_game(f"无效输入：{e.reason}")
				return

			# Bot's turn
			next_word = self._bot_move(player_word)
			if next_word is None:
				self._update_high_score()
				render_turn_info(player_word, None)
				render_game_over("你赢了！电脑接不上", self.state.current_score, self.user_state.high_score)
				return
			else:
				render_turn_info(player_word, next_word)
				# Next round starts with bot's word
				self.history.append(next_word)

	def _update_high_score(self) -> None:
		if self.state.current_score > self.user_state.high_score:
			self.user_state.high_score = self.state.current_score
		self.user_state.games_played += 1
		self.user_state.last_settings = self.settings

	def _end_game(self, reason: str):
		self._update_high_score()
		render_game_over(reason, self.state.current_score, self.user_state.high_score)