from __future__ import annotations

import re
from typing import Optional

from pypinyin import lazy_pinyin, pinyin, Style
from opencc import OpenCC

# Reuse converters
_cc_t2s = OpenCC("t2s")

# Full-width to half-width conversion
# Based on common ASCII range conversion

def to_half_width(text: str) -> str:
	result_chars = []
	for char in text:
		code = ord(char)
		if code == 0x3000:  # full-width space
			result_chars.append(" ")
		elif 0xFF01 <= code <= 0xFF5E:
			result_chars.append(chr(code - 0xFEE0))
		else:
			result_chars.append(char)
	return "".join(result_chars)


def normalize_text(text: str) -> str:
	# strip, to half width, remove inner spaces
	text = to_half_width(text)
	text = text.strip()
	# remove all whitespace inside
	text = re.sub(r"\s+", "", text)
	# convert Traditional to Simplified
	text = _cc_t2s.convert(text)
	return text


def is_four_characters(text: str) -> bool:
	return len(text) == 4


def first_char(text: str) -> str:
	return text[0]


def last_char(text: str) -> str:
	return text[-1]


def char_pinyin(ch: str, strict_tone: bool) -> str:
	if strict_tone:
		py = pinyin(ch, style=Style.TONE3, strict=False)
		# pinyin returns list of list; pick first result
		return py[0][0] if py and py[0] else ch
	else:
		py_syllables = lazy_pinyin(ch)
		return py_syllables[0] if py_syllables else ch


def char_key(ch: str, mode: str, strict_pinyin: bool) -> str:
	if mode == "char":
		return ch
	return char_pinyin(ch, strict_tone=strict_pinyin)


def first_key(word: str, mode: str, strict_pinyin: bool) -> str:
	return char_key(first_char(word), mode, strict_pinyin)


def last_key(word: str, mode: str, strict_pinyin: bool) -> str:
	return char_key(last_char(word), mode, strict_pinyin)