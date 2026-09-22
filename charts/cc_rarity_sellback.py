"""
Collector Crypt: June 2026 Sellback Rate by Rarity Tier and Machine (grouped bar)
머신 5종(Pokemon $25~$2,500) × rarity tier 4단(Common/Uncommon/Rare/Rarest).
Sellback rate = sold_back / spins per tier (June 2026).
실소스: sources/cc_rarity_gradient.csv (tier 1 = rarest per API rarity field).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(".claude/skills/design/four-pillars")
from config import create_figure, apply_style, save_chart  # noqa: E402

DATA = "outputs/data/cc_rarity_gradient.csv"
OUTDIR = "outputs/charts/collector-crypt/rarity"
FNAME = "cc_rarity_sellback"

MACHINE_ORDER = ["pokemon_25", "pokemon_50", "pokemon_250",
                 "pokemon_1000", "pokemon_2500"]
MACHINE_LABEL = {
    "pokemon_25": "Pokemon $25", "pokemon_50": "Pokemon $50",
    "pokemon_250": "Pokemon $250", "pokemon_1000": "Pokemon $1,000",
    "pokemon_2500": "Pokemon $2,500",
}
# tier 번호(rarity_tier_1_rarest) → (라벨, 색). 4=Common(가장 흔함) ... 1=Rarest
TIERS = [
    (4, "Common",   "#82e3bf"),  # 라이트 민트
    (3, "Uncommon", "#4cb389"),  # 미디엄 틸 그린
    (2, "Rare",     "#b9a3e2"),  # 라일락
    (1, "Rarest",   "#7c7ef0"),  # 페리윙클 블루
]


def main():
    df = pd.read_csv(DATA)
    piv = df.pivot(index="machine", columns="rarity_tier_1_rarest",
                   values="sellback_pct")

    x = np.arange(len(MACHINE_ORDER))
    n = len(TIERS)
    group_w = 0.82
    bar_w = group_w / n

    fig, ax = create_figure("bar")

    for i, (tier, _label, color) in enumerate(TIERS):
        vals = [piv.loc[m, tier] for m in MACHINE_ORDER]
        offset = (i - n / 2 + 0.5) * bar_w
        ax.bar(x + offset, vals, width=bar_w * 0.9, color=color, zorder=3)

    # X축
    ax.set_xticks(x)
    ax.set_xticklabels([MACHINE_LABEL[m] for m in MACHINE_ORDER])
    ax.set_xlim(-0.6, len(MACHINE_ORDER) - 0.4)

    # Y축 — 75~100%, 5% 간격
    ax.set_ylim(75, 100)
    ax.set_yticks([75, 80, 85, 90, 95, 100])
    ax.set_yticklabels([f"{v}%" for v in [75, 80, 85, 90, 95, 100]])

    apply_style(fig, ax, "bar")

    # 축 폰트 통일 (x/y 동일 14pt, x 라벨 겹침 방지 크기)
    X_FS = 14
    Y_FS = 14
    ax.tick_params(axis="x", labelsize=X_FS, rotation=0)
    ax.tick_params(axis="y", labelsize=Y_FS)
    for lbl in ax.get_xticklabels():
        lbl.set_ha("center")
        lbl.set_fontsize(X_FS)
    for lbl in ax.get_yticklabels():
        lbl.set_fontsize(Y_FS)

    Path(OUTDIR).mkdir(parents=True, exist_ok=True)
    png, svg = save_chart(fig, FNAME, OUTDIR)
    print("saved:", png, svg)


if __name__ == "__main__":
    main()
