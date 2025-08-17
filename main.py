import argparse
import json
from pathlib import Path

from src.store import load_config, merge_config, load_idioms, build_indexes, load_user_state, save_user_state
from src.game import IdiomGame
from src.models import Settings


def str2bool(v: str) -> bool:
	if isinstance(v, bool):
		return v
	lv = v.lower()
	if lv in {"yes", "true", "t", "1", "y"}:
		return True
	if lv in {"no", "false", "f", "0", "n"}:
		return False
	raise argparse.ArgumentTypeError("Expected a boolean value")


def parse_args():
	parser = argparse.ArgumentParser(description="成语接龙 - 终端版")
	parser.add_argument("--mode", choices=["char", "pinyin"], help="接龙模式：char 字接；pinyin 拼音接")
	parser.add_argument("--strict", type=str2bool, help="拼音严格模式（包含声调），默认 false")
	parser.add_argument("--timer", type=int, help="每回合计时（秒），默认 20")
	parser.add_argument("--dict", dest="dict_path", help="词库路径 JSON，默认 data/idioms.json")
	parser.add_argument("--difficulty", choices=["easy", "normal", "hard"], help="电脑难度，默认 normal")
	parser.add_argument("--allow-repeat", dest="allow_repeat", type=str2bool, help="允许重复使用同一成语，默认 false")
	return parser.parse_args()


def main():
	args = parse_args()
	config_path = Path("config.json")
	config = load_config(config_path)
	cli_overrides = {}
	if args.mode:
		cli_overrides["mode"] = args.mode
	if args.strict is not None:
		cli_overrides["strict_pinyin"] = args.strict
	if args.timer:
		cli_overrides["timer_seconds"] = int(args.timer)
	if args.dict_path:
		cli_overrides["dictionary_path"] = args.dict_path
	if args.difficulty:
		cli_overrides["difficulty"] = args.difficulty
	if args.allow_repeat is not None:
		cli_overrides["allow_repeat_idiom"] = args.allow_repeat

	settings: Settings = merge_config(config, cli_overrides)

	idioms = load_idioms(settings.dictionary_path)
	indexes = build_indexes(idioms, settings.mode, settings.strict_pinyin)

	user_state = load_user_state(settings.save_path)
	game = IdiomGame(settings=settings, indexes=indexes, idioms=idioms, user_state=user_state)
	try:
		game.run()
	finally:
		save_user_state(settings.save_path, game.user_state)


if __name__ == "__main__":
	main()