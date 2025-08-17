from __future__ import annotations

from typing import Iterable, Optional, Set

from .models import Settings
from .utils import normalize_text, is_four_characters, first_key, last_key


class ValidationErrorInfo(Exception):
	def __init__(self, reason: str):
		super().__init__(reason)
		self.reason = reason


def ensure_valid_user_input(raw: str) -> str:
	if not raw:
		raise ValidationErrorInfo("输入为空")
	word = normalize_text(raw)
	if not is_four_characters(word):
		raise ValidationErrorInfo("必须是四字成语")
	return word


def check_in_dictionary(word: str, dictionary_words: Set[str]) -> None:
	if word not in dictionary_words:
		raise ValidationErrorInfo("成语不在词库中")


def can_chain(prev_word: str, new_word: str, settings: Settings) -> bool:
	# Compare last char/key of prev and first char/key of new
	prev_last = last_key(prev_word, settings.mode, settings.strict_pinyin)
	new_first = first_key(new_word, settings.mode, settings.strict_pinyin)
	return prev_last == new_first


def ensure_chain(prev_word: str, new_word: str, settings: Settings) -> None:
	if not can_chain(prev_word, new_word, settings):
		if settings.mode == "char":
			raise ValidationErrorInfo("首尾汉字不匹配")
		else:
			raise ValidationErrorInfo("首尾拼音不匹配")


def ensure_not_repeated(word: str, used: Set[str], allow_repeat: bool) -> None:
	if not allow_repeat and word in used:
		raise ValidationErrorInfo("成语已使用，且未开启允许重复")