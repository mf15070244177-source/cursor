from src.rules import ensure_valid_user_input, check_in_dictionary, can_chain, ValidationErrorInfo
from src.models import Settings


def test_ensure_valid_user_input_ok():
	assert ensure_valid_user_input(" 一鸣惊人 ") == "一鸣惊人"


def test_ensure_valid_user_input_len_error():
	try:
		ensure_valid_user_input("不是四字词")
	except ValidationErrorInfo as e:
		assert "四字" in e.reason
	else:
		assert False


def test_check_in_dictionary():
	dict_words = {"掩耳盗铃", "一鸣惊人"}
	check_in_dictionary("一鸣惊人", dict_words)
	try:
		check_in_dictionary("东拉西扯", dict_words)
	except ValidationErrorInfo as e:
		assert "不在词库" in e.reason
	else:
		assert False


def test_can_chain_char_mode():
	settings = Settings(mode="char")
	assert can_chain("一鸣惊人", "人山人海", settings) is True
	assert can_chain("画蛇添足", "足智多谋", settings) is True
	assert can_chain("画蛇添足", "人山人海", settings) is False


def test_can_chain_pinyin_mode():
	settings = Settings(mode="pinyin", strict_pinyin=False)
	# 尾字“人”-> 首字“仁”，无声调模式下拼音 ren -> ren，应当允许
	assert can_chain("一鸣惊人", "仁人君子", settings) is True