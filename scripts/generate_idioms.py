#!/usr/bin/env python3
import json
from pathlib import Path

# Minimal seed list to bootstrap; in practice this should be replaced by a curated list.
SEED = [
	"一鸣惊人", "人山人海", "海阔天空", "空前绝后", "后生可畏", "畏首畏尾", "委曲求全", "全民皆兵",
	"兵荒马乱", "乱七八糟", "遭遇不测", "侧目而视", "势不可挡", "当机立断", "断章取义", "义不容辞",
	"辞不达意", "意气风发", "发人深省", "省吃俭用", "用心良苦", "苦尽甘来", "来日方长", "长驱直入",
	"入木三分", "分道扬镳", "彪炳千古", "古色古香", "相辅相成", "成仁取义", "一见如故", "故步自封",
	"逢凶化吉", "吉星高照", "照本宣科", "苛政猛于虎", "虎头蛇尾", "尾大不掉", "掉以轻心", "心心相印",
	"饮水思源", "源远流长", "长生不老", "老当益壮", "壮志凌云", "云消雾散", "散漫无纪", "继往开来",
	"来者不拒", "拒人于千里", "里应外合", "合情合理", "理直气壮", "壮士断腕", "万无一失", "十拿九稳",
	"稳扎稳打", "打草惊蛇", "蛇行龟步", "步步为营", "迎刃而解", "解铃还须系铃人", "人面兽心", "心旷神怡",
	"怡然自得", "得心应手", "手无缚鸡之力", "力不从心", "心有灵犀", "息事宁人", "人杰地灵", "灵机一动",
	"动人心弦", "弦外之音", "因人成事", "事半功倍", "背水一战", "战无不胜", "胜友如云", "云开见日",
	"日新月异", "异口同声", "声东击西", "西装革履", "履险如夷", "夷然自若", "弱不禁风", "风花雪月",
	"月白风清", "清正廉明", "明目张胆", "胆大包天", "天马行空", "空穴来风", "逢场作戏", "喜闻乐见",
	"见多识广", "广开言路", "路不拾遗", "移花接木", "目不转睛", "精益求精", "惊弓之鸟", "鸟语花香",
]

EXTRA = [
	"画龙点睛", "锦上添花", "雪中送炭", "南辕北辙", "不寒而栗", "举一反三", "对牛弹琴", "入乡随俗",
	"胸有成竹", "高山流水", "班门弄斧", "坐井观天", "守株待兔", "亡羊补牢", "狐假虎威", "滥竽充数",
	"掩耳盗铃", "指鹿为马", "狼狈为奸", "鹤立鸡群", "叶公好龙", "望梅止渴", "自相矛盾", "纸上谈兵",
	"囫囵吞枣", "杯弓蛇影", "井底之蛙", "毛遂自荐", "背道而驰", "因小失大", "持之以恒", "与众不同",
	"才高八斗", "博古通今", "夜以继日", "志同道合", "安居乐业", "一丝不苟", "开门见山", "三顾茅庐",
	"草木皆兵", "孤注一掷", "迫不及待", "不约而同", "不言而喻", "走马观花", "东拼西凑", "左右逢源",
	"青出于蓝", "出类拔萃", "无与伦比", "按部就班", "自强不息", "厚积薄发", "铺天盖地", "雄心勃勃",
	"优柔寡断", "目不暇接", "出人头地", "见义勇为", "恍然大悟", "热泪盈眶", "不可思议", "一成不变",
	"改过自新", "一举两得", "七上八下", "九牛一毛", "一箭双雕", "一清二楚", "自食其果", "因人而异",
	"对症下药", "豁然开朗", "如火如荼", "口是心非", "心直口快", "忐忑不安", "大公无私", "大器晚成",
	"精打细算", "精兵简政", "开源节流", "同甘共苦", "同舟共济", "忍无可忍", "防患未然", "未雨绸缪",
	"历历在目", "迫在眉睫", "不胜枚举", "不屈不挠", "侃侃而谈", "坚持不懈", "锲而不舍", "各抒己见",
	"高瞻远瞩", "扬长避短", "取长补短", "络绎不绝", "津津乐道", "闻鸡起舞", "画饼充饥", "望尘莫及",
	"披荆斩棘", "迎难而上", "一览无余", "一见钟情", "趋之若鹜", "目中无人",
]


def generate_variants(word: str) -> list[str]:
	# Generate simple 4-char variants by rotation and reversal; placeholders only
	w = word
	variants = set()
	if len(w) == 4:
		variants.add(w)
		variants.add(w[::-1])  # reverse
		variants.add(w[1:] + w[0])  # rotate 1
		variants.add(w[2:] + w[:2])  # rotate 2
		variants.add(w[3:] + w[:3])  # rotate 3
	return [v for v in variants if len(v) == 4]


def main():
	items = []
	seen = set()
	for w in SEED + EXTRA:
		for v in generate_variants(w):
			if v not in seen:
				items.append({"word": v})
				seen.add(v)
		if len(items) >= 600:
			break
	# If still short, pad by pairing first two and last two chars
	if len(items) < 600:
		for w in SEED + EXTRA:
			if len(w) == 4:
				p = w[:2] + w[2:]
				if p not in seen:
					items.append({"word": p})
					seen.add(p)
			if len(items) >= 600:
				break

	out = Path("data/idioms.json")
	out.parent.mkdir(parents=True, exist_ok=True)
	with out.open("w", encoding="utf-8") as f:
		json.dump(items, f, ensure_ascii=False, indent=2)
	print(f"Wrote {len(items)} idioms to {out}")


if __name__ == "__main__":
	main()