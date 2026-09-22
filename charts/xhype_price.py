import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from pathlib import Path
import json
import sys

sys.path.append('.claude/skills/design/four-pillars')
from config import create_figure, apply_style, COLORS, DPI

mpl.rcParams['axes.unicode_minus'] = False

# =============================================================================
# APY 데이터 → Share Price 역산
# =============================================================================
apy_data = json.loads('''[{"timestamp":1764028799999,"trailing3d":0.6934937585526546,"trailing7d":0.6934937585526546,"trailing30d":0.6934937585526546},{"timestamp":1764115199999,"trailing3d":13.504878456095549,"trailing7d":13.504878456095549,"trailing30d":13.504878456095549},{"timestamp":1764201599999,"trailing3d":9.185750661578265,"trailing7d":9.185750661578265,"trailing30d":9.185750661578265},{"timestamp":1764287999999,"trailing3d":9.549996005731476,"trailing7d":7.336433972093714,"trailing30d":7.336433972093714},{"timestamp":1764374399999,"trailing3d":4.789813409486698,"trailing7d":8.278125496870503,"trailing30d":8.278125496870503},{"timestamp":1764460799999,"trailing3d":4.607449999681286,"trailing7d":6.898437914058753,"trailing30d":6.898437914058753},{"timestamp":1764547199999,"trailing3d":4.060349560811027,"trailing7d":5.933803738624224,"trailing30d":5.933803738624224},{"timestamp":1764633599999,"trailing3d":7.972189426509753,"trailing7d":9.228824523803565,"trailing30d":8.16680149878736},{"timestamp":1764719999999,"trailing3d":7.972189426509753,"trailing7d":5.469429786855621,"trailing30d":7.259379110033209},{"timestamp":1764806399999,"trailing3d":8.020736867439462,"trailing7d":5.432913416270581,"trailing30d":6.562640936231679},{"timestamp":1764892799999,"trailing3d":10.26229015229463,"trailing7d":9.534093443759202,"trailing30d":8.74333040093599},{"timestamp":1764979199999,"trailing3d":10.28655931795175,"trailing7d":7.825178033340644,"trailing30d":8.020802812774692},{"timestamp":1765065599999,"trailing3d":10.237939007343822,"trailing7d":7.84598013384024,"trailing30d":7.415048649177951},{"timestamp":1765151999999,"trailing3d":0.12134544101405353,"trailing7d":7.84594882098907,"trailing30d":6.89583079466588},{"timestamp":1765238399999,"trailing3d":2.7423889488548867,"trailing7d":5.5838349714885585,"trailing30d":6.966570634197884},{"timestamp":1765324799999,"trailing3d":2.6938507143558312,"trailing7d":5.5838349714885585,"trailing30d":6.531159969560517},{"timestamp":1765411199999,"trailing3d":2.6453126734979535,"trailing7d":5.542195595014137,"trailing30d":6.146974088998134},{"timestamp":1765497599999,"trailing3d":4.403852136663796,"trailing7d":3.073075821932487,"trailing30d":6.541552237141225},{"timestamp":1765583999999,"trailing3d":4.403852136663796,"trailing7d":3.0626747509365786,"trailing30d":6.197260014133793},{"timestamp":1765670399999,"trailing3d":4.403852136663796,"trailing7d":3.041872650436983,"trailing30d":5.887397013427104},{"timestamp":1765756799999,"trailing3d":6.754980969894723,"trailing7d":5.91606247716706,"trailing30d":6.575155109318276},{"timestamp":1765843199999,"trailing3d":6.767101674847139,"trailing7d":4.787551633504686,"trailing30d":6.277943498508363},{"timestamp":1765929599999,"trailing3d":6.767101674847139,"trailing7d":4.787551633504686,"trailing30d":6.004989433355826},{"timestamp":1766015999999,"trailing3d":5.6724842792488985,"trailing7d":7.213421736774607,"trailing30d":6.465004314961317},{"timestamp":1766102399999,"trailing3d":5.854204478711249,"trailing7d":5.409131208667881,"trailing30d":6.229763932124621},{"timestamp":1766188799999,"trailing3d":5.866319342223259,"trailing7d":5.414323293030171,"trailing30d":5.991561460562456},{"timestamp":1766275199999,"trailing3d":4.5309577345152094,"trailing7d":7.267895564425214,"trailing30d":6.2522585444881535},{"timestamp":1766361599999,"trailing3d":4.349227376493199,"trailing7d":4.378093954352941,"trailing30d":6.030267156167156},{"timestamp":1766447999999,"trailing3d":4.4218862533613,"trailing7d":4.409230969536239,"trailing30d":5.831137174937864},{"timestamp":1766534399999,"trailing3d":4.9410642699571445,"trailing7d":6.485308105186644,"trailing30d":6.123428222479503},{"timestamp":1766620799999,"trailing3d":4.941059353643825,"trailing7d":4.064626129093624,"trailing30d":6.087831717604084},{"timestamp":1766707199999,"trailing3d":4.856285613263715,"trailing7d":3.9815514557730105,"trailing30d":5.21063961231623},{"timestamp":1766793599999,"trailing3d":4.575923629244158,"trailing7d":5.932281371052744,"trailing30d":5.648785071252161},{"timestamp":1766879999999,"trailing3d":4.5759190779821965,"trailing7d":4.083895276293762,"trailing30d":5.590424024829155},{"timestamp":1766966399999,"trailing3d":4.648525478685624,"trailing7d":4.1098220709983355,"trailing30d":5.1965108192361225},{"timestamp":1767052799999,"trailing3d":5.191327187696918,"trailing7d":6.262041771482295,"trailing30d":5.707172790053724},{"timestamp":1767139199999,"trailing3d":5.7598301558094605,"trailing7d":4.434794941659041,"trailing30d":5.760372084328998},{"timestamp":1767225599999,"trailing3d":5.711414435995987,"trailing7d":4.439974249149262,"trailing30d":4.970433320184745},{"timestamp":1767311999999,"trailing3d":7.716840768224874,"trailing7d":7.487993980751363,"trailing30d":5.681637924225236},{"timestamp":1767398399999,"trailing3d":7.208766222423428,"trailing7d":5.563156053021585,"trailing30d":5.679175019827395},{"timestamp":1767484799999,"trailing3d":7.426339104054769,"trailing7d":5.661582831751793,"trailing30d":4.686838215360761},{"timestamp":1767571199999,"trailing3d":0.7736347048736455,"trailing7d":5.827326506260516,"trailing30d":4.730345462917426},{"timestamp":1767657599999,"trailing3d":6.35804658078587,"trailing7d":6.063178650059706,"trailing30d":5.291185777171601},{"timestamp":1767743999999,"trailing3d":6.1766923385751324,"trailing7d":5.840238052937081,"trailing30d":5.292372905116868},{"timestamp":1767830399999,"trailing3d":12.833533297438303,"trailing7d":8.879663161164364,"trailing30d":5.739459897775768},{"timestamp":1767916799999,"trailing3d":7.176591920397509,"trailing7d":5.831643429562264,"trailing30d":5.739459897775768},{"timestamp":1768003199999,"trailing3d":7.116182600086951,"trailing7d":5.800559357650019,"trailing30d":5.739459897775768},{"timestamp":1768089599999,"trailing3d":6.496211012230783,"trailing7d":8.481036836096942,"trailing30d":5.9486957853324665},{"timestamp":1768175999999,"trailing3d":6.4479378203499875,"trailing7d":8.263487621909267,"trailing30d":5.943868466144388},{"timestamp":1768262399999,"trailing3d":6.472074512057372,"trailing7d":5.849428471052091,"trailing30d":5.946282135315126},{"timestamp":1768348799999,"trailing3d":5.0324903807068555,"trailing7d":7.99066456843911,"trailing30d":5.77644672641368},{"timestamp":1768435199999,"trailing3d":5.237586579730132,"trailing7d":5.008081885748624,"trailing30d":5.790916956632687},{"timestamp":1768521599999,"trailing3d":5.3220182628016905,"trailing7d":5.054611189225313,"trailing30d":5.801773794110582},{"timestamp":1768607999999,"trailing3d":5.331870327775008,"trailing7d":7.22595930887685,"trailing30d":5.742385331266291},{"timestamp":1768694399999,"trailing3d":5.271511511605616,"trailing7d":4.48321067119498,"trailing30d":5.732647659922122},{"timestamp":1768780799999,"trailing3d":5.175001065096793,"trailing7d":4.509066865545372,"trailing30d":5.732641966397933},{"timestamp":1768867199999,"trailing3d":4.389082412621889,"trailing7d":6.3332484091187835,"trailing30d":5.728197799076958},{"timestamp":1768953599999,"trailing3d":5.027892427906244,"trailing7d":4.481240119994718,"trailing30d":5.8005141650634275},{"timestamp":1769039999999,"trailing3d":5.064046288077402,"trailing7d":4.43469245483706,"trailing30d":5.796857969869544},{"timestamp":1769126399999,"trailing3d":5.725174728078357,"trailing7d":6.506029751380213,"trailing30d":5.80660884488908},{"timestamp":1769212799999,"trailing3d":5.050140551106751,"trailing7d":4.360498787136893,"trailing30d":5.81142228480972},{"timestamp":1769299199999,"trailing3d":5.158552063327049,"trailing7d":4.386281262717673,"trailing30d":5.827084614875877},{"timestamp":1769385599999,"trailing3d":8.072023134818103,"trailing7d":7.747610638403633,"trailing30d":6.156218795446473},{"timestamp":1769471999999,"trailing3d":8.011783105532261,"trailing7d":5.9130847983841965,"trailing30d":6.1550086875647265},{"timestamp":1769558399999,"trailing3d":7.903319875753989,"trailing7d":5.618607311795278,"trailing30d":6.152564054582714},{"timestamp":1769644799999,"trailing3d":6.3811843233406345,"trailing7d":8.312098367802161,"trailing30d":6.275204509010845},{"timestamp":1769731199999,"trailing3d":6.405251735830805,"trailing7d":6.204546373135246,"trailing30d":6.21955084556686},{"timestamp":1769817599999,"trailing3d":6.357091664947505,"trailing7d":6.178729217727029,"trailing30d":6.2171317774778645},{"timestamp":1769903999999,"trailing3d":4.3922941389377135,"trailing7d":7.983702114492444,"trailing30d":5.942749846082131},{"timestamp":1769990399999,"trailing3d":4.440402907517164,"trailing7d":4.648137704291986,"trailing30d":5.9427145140762345},{"timestamp":1770076799999,"trailing3d":4.572725121171499,"trailing7d":4.704847224429558,"trailing30d":5.9317703791895395},{"timestamp":1770163199999,"trailing3d":6.12284576592248,"trailing7d":7.220641781707512,"trailing30d":6.4776709521870135},{"timestamp":1770249599999,"trailing3d":6.062692897564855,"trailing7d":4.511641378959509,"trailing30d":5.913179145754133},{"timestamp":1770335999999,"trailing3d":6.399279416185454,"trailing7d":4.702287658867266,"trailing30d":5.9540290869505705},{"timestamp":1770422399999,"trailing3d":8.428027607441472,"trailing7d":8.10818575706207,"trailing30d":6.03712038318733},{"timestamp":1770508799999,"trailing3d":8.572199157448964,"trailing7d":6.30302924403576,"trailing30d":6.052739869459278},{"timestamp":1770595199999,"trailing3d":8.211423941921646,"trailing7d":6.318439530754901,"trailing30d":6.06355322113404},{"timestamp":1770681599999,"trailing3d":6.47594296804906,"trailing7d":8.923850548581026,"trailing30d":6.035093578769158},{"timestamp":1770767999999,"trailing3d":6.4038082878135425,"trailing7d":6.423441753417643,"trailing30d":6.0483269162056335},{"timestamp":1770854399999,"trailing3d":6.343708829187296,"trailing7d":6.438874930021662,"trailing30d":6.050716652847032},{"timestamp":1770940799999,"trailing3d":6.844827361140486,"trailing7d":9.114799667847468,"trailing30d":6.21632727681252},{"timestamp":1771027199999,"trailing3d":6.772769023980941,"trailing7d":5.714045217648845,"trailing30d":6.201845160630714},{"timestamp":1771113599999,"trailing3d":6.724734965859569,"trailing7d":5.647104562197636,"trailing30d":6.19098832315282},{"timestamp":1771199999999,"trailing3d":6.396977259649309,"trailing7d":8.337179661159322,"trailing30d":6.32283796999995},{"timestamp":1771286399999,"trailing3d":6.384975414324885,"trailing7d":5.675059123195626,"trailing30d":6.3131915509026415},{"timestamp":1771372799999,"trailing3d":6.384975414324885,"trailing7d":5.639033330702497,"trailing30d":6.31198575807563},{"timestamp":1771459199999,"trailing3d":4.390367024036242,"trailing7d":7.5000331732374415,"trailing30d":6.322966431141386},{"timestamp":1771545599999,"trailing3d":4.414349446563308,"trailing7d":4.633425731233978,"trailing30d":6.251837252768349},{"timestamp":1771631999999,"trailing3d":4.426340634188342,"trailing7d":4.633421163648525,"trailing30d":6.248215192686724},{"timestamp":1771718399999,"trailing3d":4.232885143200675,"trailing7d":6.432097534955057,"trailing30d":6.173737472653618},{"timestamp":1771804799999,"trailing3d":4.220889761533268,"trailing7d":3.700816803469961,"trailing30d":6.168912173810999},{"timestamp":1771891199999,"trailing3d":4.244859661056477,"trailing7d":3.716228697962065,"trailing30d":6.156845952459667},{"timestamp":1771977599999,"trailing3d":3.8478251053309194,"trailing7d":5.344747402529072,"trailing30d":5.751317669704901},{"timestamp":1772063999999,"trailing3d":3.8358380644712606,"trailing7d":3.4631615350849683,"trailing30d":5.751317669704901},{"timestamp":1772150399999,"trailing3d":3.9316927386147853,"trailing7d":3.5093758231269843,"trailing30d":5.7596832387457475},{"timestamp":1772236799999,"trailing3d":3.2953597578950045,"trailing7d":4.860041312689071,"trailing30d":5.442735213160337},{"timestamp":1772323199999,"trailing3d":3.3672397950360224,"trailing7d":3.0921706715858326,"trailing30d":5.447516475625423},{"timestamp":1772409599999,"trailing3d":3.5109625482513764,"trailing7d":3.205121303149031,"trailing30d":5.475070327076136},{"timestamp":1772495999999,"trailing3d":1.6532019396312547,"trailing7d":3.74933086064969,"trailing30d":5.168825993229691},{"timestamp":1772582399999,"trailing3d":1.6891273092999315,"trailing7d":2.1670144732868373,"trailing30d":5.172388915803698},{"timestamp":1772668799999,"trailing3d":1.497436701582126,"trailing7d":2.202949290482259,"trailing30d":5.167541485117197},{"timestamp":1772755199999,"trailing3d":0.5030862496824643,"trailing7d":2.2799280796786947,"trailing30d":4.606850041605688},{"timestamp":1772841599999,"trailing3d":0.5030817921127065,"trailing7d":0.9703239165229955,"trailing30d":4.616427805258484},{"timestamp":1772927999999,"trailing3d":0.4791227709319834,"trailing7d":0.9651848515805282,"trailing30d":4.57552582059185},{"timestamp":1773014399999,"trailing3d":3.1980525299981633,"trailing7d":2.145823786141603,"trailing30d":4.083852533861358},{"timestamp":1773100799999,"trailing3d":3.1142010519666186,"trailing7d":1.596466393238151,"trailing30d":4.0706279947102475},{"timestamp":1773187199999,"trailing3d":3.0662868783899087,"trailing7d":1.5553960954762327,"trailing30d":4.061012114238675},{"timestamp":1773273599999,"trailing3d":0.0359241832402768,"trailing7d":1.519461278280811,"trailing30d":3.4398506553804795}]''')

# timestamp → date, trailing3d APY → daily return → cumulative price
df = pd.DataFrame(apy_data)
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
df = df.sort_values('date').reset_index(drop=True)

# trailing3d APY → 일일 수익률
# daily_return = (1 + APY/100)^(1/365) - 1
df['daily_return'] = (1 + df['trailing3d'] / 100) ** (1/365) - 1

# 누적 가격 (시작 $1.00)
prices = [1.0]
for i in range(1, len(df)):
    prices.append(prices[-1] * (1 + df['daily_return'].iloc[i]))
df['raw_price'] = prices

# 실제 최종 가격 $1.01603에 맞게 보정
target_final = 1.01603
raw_final = df['raw_price'].iloc[-1]
# 보정 계수 적용 (로그 스케일 보정)
n = len(df) - 1
if raw_final != 1.0:
    log_ratio = np.log(target_final) / np.log(raw_final)
    df['price'] = df['raw_price'] ** log_ratio
else:
    df['price'] = df['raw_price']

print(f"Date range: {df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}")
print(f"Raw price: $1.00 → ${raw_final:.5f}")
print(f"Calibrated price: $1.00 → ${df['price'].iloc[-1]:.5f}")
print(f"Data points: {len(df)}")

# CSV 저장
output_data_dir = 'outputs/data'
Path(output_data_dir).mkdir(parents=True, exist_ok=True)
df[['date', 'price', 'trailing3d', 'trailing7d', 'trailing30d']].to_csv(
    f'{output_data_dir}/xhype_price.csv', index=False
)

# =============================================================================
# 차트 생성
# =============================================================================
fig, ax = create_figure('line')

fig.patch.set_alpha(0)
ax.set_facecolor('none')

# Liminal 민트 그린 (#4ade80에 가까운 색)
mint_green = '#4ade80'

# 라인
ax.plot(df['date'], df['price'], color=mint_green, linewidth=1.8)

# 영역 채우기 (그라데이션 효과)
ax.fill_between(df['date'], df['price'], df['price'].min() * 0.9999,
                color=mint_green, alpha=0.15)

# Y축
y_min = df['price'].min()
y_max = df['price'].max()
y_range = y_max - y_min
ax.set_ylim(y_min - y_range * 0.05, y_max + y_range * 0.15)

# Y축 포맷: $1.00000 스타일
def price_formatter(x, pos):
    return f'${x:.3f}'
ax.yaxis.set_major_formatter(mticker.FuncFormatter(price_formatter))
ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5))

# X축
ax.set_xlim(df['date'].iloc[0], df['date'].iloc[-1])
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# 스타일
apply_style(fig, ax, 'line')

ax.tick_params(axis='y', labelsize=16, length=0, pad=15)
ax.tick_params(axis='x', labelsize=14, length=0, pad=15)
ax.grid(True, axis='y', color='#404040', alpha=0.8,
        linestyle=(0, (3.7, 1.6)), linewidth=1.0)
ax.set_axisbelow(True)

for spine in ax.spines.values():
    spine.set_visible(False)

# =============================================================================
# 저장
# =============================================================================
output_dir = 'outputs/charts/liminal'
Path(output_dir).mkdir(parents=True, exist_ok=True)

png_path = f"{output_dir}/xhype_price.png"
svg_path = f"{output_dir}/xhype_price.svg"

fig.savefig(png_path, dpi=DPI, facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', facecolor='none', edgecolor='none',
            bbox_inches='tight', transparent=True)

plt.close(fig)
print(f"\nPNG: {png_path}")
print(f"SVG: {svg_path}")
