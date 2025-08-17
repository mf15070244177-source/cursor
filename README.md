# 成语接龙（离线终端版 / Python）

一款可在 macOS 本地离线运行的「成语接龙」游戏。终端彩色界面、可配置、带人机对战与得分机制，内置 ≥500 条成语词库，支持扩展自定义词库。默认仅使用本地资源，无需联网。

### 功能亮点
- 四字成语接龙：首尾字（或首尾拼音）匹配
- 词库校验：仅允许词库中存在的成语
- 计时与得分：每回合默认 20 秒；连对有加成
- 人机对战：电脑基于出度表的策略（易/普/难）
- 可选模式：字接（默认）/ 拼音接（pypinyin）/ 是否允许重复
- 简繁体与全半角归一：输入自动规范化
- 提示与悔步：:hint、:undo
- 本地存档：最高分与最后设置保存到 `data/user_state.json`

## 目录结构
```
.
├── config.json               # 默认配置
├── data/
│   ├── idioms.json           # ≥500 条四字成语（可替换/扩展）
│   └── user_state.json       # 运行后自动生成
├── main.py                   # 入口脚本
├── requirements.txt
├── scripts/
│   └── generate_idioms.py    # 词库占位生成脚本（已生成完成可忽略）
├── src/
│   ├── __init__.py
│   ├── engine.py             # 电脑策略
│   ├── game.py               # 主循环
│   ├── io_cli.py             # 终端交互
│   ├── models.py             # 数据模型
│   ├── rules.py              # 规则与校验
│   └── store.py              # 读写/索引构建
└── tests/
    ├── test_rules.py
    └── test_store.py
```

## 快速开始（macOS，Apple Silicon & Intel）
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --mode char
# 可选：
python main.py --mode pinyin --strict false --timer 20 --dict data/idioms.json
pytest -q
```

- 首次运行会在 `data/` 下生成/更新 `user_state.json`。
- 若需重新生成占位词库，可执行：
```bash
python scripts/generate_idioms.py
```

## 玩法说明
- 只允许四字成语。
- 新成语首字需要与上一成语尾字相同；在拼音模式下比较首尾字拼音（默认忽略声调，`--strict true` 可启用声调）。
- 忽略简繁、空格与全半角差异。
- 词库校验：玩家输入的成语必须存在于词库中。
- 失败条件：超时 / 无效成语 / 电脑接不上（你赢了）。
- 计分：基础分 10 + 连续连对 ×2 加成。
- 命令：
  - `:hint` 提示（有限次数）
  - `:undo` 悔步（仅撤销玩家上一步）
  - `:help` 帮助
  - `:quit` 退出

## 配置项（config.json / 命令行覆盖）
- mode: `char` | `pinyin`
- strict_pinyin: true|false（拼音模式下是否包含声调）
- timer_seconds: 每回合秒数（默认 20）
- difficulty: `easy` | `normal` | `hard`
- allow_repeat_idiom: 是否允许重复使用同一成语
- dictionary_path: 词库路径
- max_hints: 提示次数
- save_path: 存档路径

示例命令行（覆盖配置）：
```bash
python main.py --mode pinyin --strict false --timer 15 --dict data/idioms.json --difficulty hard --allow-repeat false
```

## 词库格式与扩展
- 文件路径：`data/idioms.json`
- UTF-8 编码
- 结构示例：
```json
[
  {"word": "一鸣惊人", "pinyin": "yi ming jing ren"},
  {"word": "人山人海"}
]
```
- 可通过 `--dict path/to.json` 指定外部词库。
- 启动时会构建首字/尾字索引与出度表，提升检索效率。

## 测试与验收
- 运行：`pytest -q`
- 覆盖：规则校验、索引构建、存储持久化等。
- 示例对局：
  - 玩家：一鸣惊人 → 电脑：人山人海 → 玩家：海阔天空 → ...

## 常见问题
- 终端无彩色/中文显示异常：尝试更换字体或终端编码为 UTF-8。
- 拼音接龙失效：确认已安装 `pypinyin`，并在命令中使用 `--mode pinyin`。
- 词库数量不足：可替换 `data/idioms.json` 为更大词库，或运行 `python scripts/generate_idioms.py` 生成占位集。

## 扩展建议
- 更大更权威的成语词库与拼音注音
- 难度曲线与关卡设计、道具（跳过/冻结时间）
- Web（Vite+React+TS）与 macOS 原生（SwiftUI）版本
- 存档与复盘、排行榜、多人对战（离线/联机）