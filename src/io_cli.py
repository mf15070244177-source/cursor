from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from inputimeout import inputimeout, TimeoutOccurred


console = Console()


@dataclass
class TurnResult:
	user_input: Optional[str]
	timeout: bool


def render_header():
	console.print(Panel.fit("[bold cyan]成语接龙[/bold cyan] - 终端版", border_style="cyan"))


def render_status(score: int, streak: int, remaining_hints: int, mode: str, difficulty: str):
	table = Table(title="状态", show_header=False, expand=True)
	table.add_row("分数", str(score), "连对", str(streak), "剩余提示", str(remaining_hints), "模式", mode, "难度", difficulty)
	console.print(table)


def render_turn_info(prev_word: Optional[str], bot_word: Optional[str]):
	if prev_word:
		console.print(Text(f"你：{prev_word}", style="bold green"))
	if bot_word:
		console.print(Text(f"电脑：{bot_word}", style="bold magenta"))


def read_user_input_with_timeout(prompt: str, seconds: int) -> TurnResult:
	try:
		value = inputimeout(prompt=prompt, timeout=seconds)
		return TurnResult(user_input=value, timeout=False)
	except TimeoutOccurred:
		return TurnResult(user_input=None, timeout=True)


def render_error(reason: str):
	console.print(Panel.fit(f"[bold red]无效：[/bold red]{reason}", border_style="red"))


def render_info(message: str):
	console.print(Panel.fit(message, border_style="blue"))


def render_hint_list(hints: List[str]):
	if not hints:
		console.print(Text("没有可用提示", style="yellow"))
		return
	console.print(Text("提示：", style="bold cyan"))
	for w in hints:
		console.print(f" - {w}")


def render_game_over(reason: str, score: int, high_score: int):
	console.print(Panel.fit(f"[bold red]游戏结束：[/bold red]{reason}\n本局得分：{score}，历史最高：{high_score}", border_style="red"))


def render_help():
	console.print("命令：[:hint] 提示，[:undo] 悔步，[:quit] 退出，[:help] 帮助")