"""Blockworks 'Daily active traders (Solana)' 차트를 픽셀 역산해 일별 CSV로 만든다.

확대본(2000x1197)이라 하루가 3.16px. 축 보정값은 그리드/틱 좌표에서 직접 측정.
"""
import numpy as np
import pandas as pd
from PIL import Image

SRC = '/Users/a./.claude/image-cache/b3c3892c-573c-4e61-af3d-3972774e66cf/5.png'
Y0, PX20 = 1085.0, (1085.0 - 217.5) / 4        # $0K 행, 20K당 픽셀
X0, PXD = 457.5, (1610.0 - 457.5) / 365.0      # 2025-08-01 열, 하루당 픽셀
D0 = pd.Timestamp('2025-08-01')

im = np.array(Image.open(SRC).convert('RGB')).astype(int)
r, g, b = im[:, :, 0], im[:, :, 1], im[:, :, 2]
mint = (g > 110) & (b > 100) & (g > r + 20)
xs = np.nonzero(mint.any(axis=0))[0]
CAP = 5                                        # 라인 둥근 캡이 양끝을 부풀린 만큼

val = lambda y: (Y0 - y) / PX20 * 20000
day = lambda x: D0 + pd.Timedelta(days=(x - X0) / PXD)

rows = [(day(x), val(np.median(np.nonzero(mint[:, x])[0])))
        for x in range(xs.min() + CAP, xs.max() - CAP + 1) if mint[:, x].any()]
s = pd.Series([v for _, v in rows], index=[d for d, _ in rows]).sort_index()
daily = s.resample('D').mean().interpolate().clip(lower=0).round(0)
daily.index.name = 'date'

# 마지막 이틀은 하루 만에 57K -> 83K로 튀어 선이 거의 수직이다. 굵기 10px에 가로로
# 번져서 열 중앙값이 두 점을 평균내버리므로, 세그먼트 양 끝값을 그대로 박는다.
daily.loc['2026-09-04'] = 56_991
daily.loc['2026-09-05'] = 82_997

assert abs(daily['2025-08'].mean() - 1100) < 100, daily['2025-08'].mean()  # 부제 "about 1,100"
daily.to_csv('outputs/data/fomo_daily_active_traders_solana.csv',
             header=['active_traders'])
print(daily.index[0].date(), '~', daily.index[-1].date(),
      '| peak', int(daily.max()), daily.idxmax().date(), '| last', int(daily.iloc[-1]))
