import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path
import json

# ── Font ──
font_path = Path('/Users/ijaheun/Desktop/Project/data/assets/font/SUIT/SUIT-ttf/')
font_bold = fm.FontProperties(fname=str(font_path / 'SUIT-Bold.ttf'))

# ── Data (ASXN API daily OI, fetched 2026-03-06) ──
raw = json.loads("""[{"date":"2025-10-13","dex_oi":{"xyz":13760394}},{"date":"2025-10-14","dex_oi":{"xyz":14105183}},{"date":"2025-10-15","dex_oi":{"xyz":14809206}},{"date":"2025-10-16","dex_oi":{"xyz":15462807}},{"date":"2025-10-17","dex_oi":{"xyz":12039909}},{"date":"2025-10-18","dex_oi":{"xyz":12092978}},{"date":"2025-10-19","dex_oi":{"xyz":13285325}},{"date":"2025-10-20","dex_oi":{"xyz":13766255}},{"date":"2025-10-21","dex_oi":{"xyz":17217030}},{"date":"2025-10-22","dex_oi":{"xyz":23615250}},{"date":"2025-10-23","dex_oi":{"xyz":24690739}},{"date":"2025-10-24","dex_oi":{"xyz":26615609}},{"date":"2025-10-25","dex_oi":{"xyz":39004877}},{"date":"2025-10-26","dex_oi":{"xyz":47144493}},{"date":"2025-10-27","dex_oi":{"xyz":55709580}},{"date":"2025-10-28","dex_oi":{"xyz":66796454}},{"date":"2025-10-29","dex_oi":{"xyz":73901718}},{"date":"2025-10-30","dex_oi":{"xyz":64577897}},{"date":"2025-10-31","dex_oi":{"xyz":64077843}},{"date":"2025-11-01","dex_oi":{"xyz":65280756}},{"date":"2025-11-02","dex_oi":{"xyz":65158238}},{"date":"2025-11-03","dex_oi":{"xyz":61288146}},{"date":"2025-11-04","dex_oi":{"xyz":56531164}},{"date":"2025-11-05","dex_oi":{"xyz":56847291}},{"date":"2025-11-06","dex_oi":{"xyz":59496120}},{"date":"2025-11-07","dex_oi":{"xyz":60742862}},{"date":"2025-11-08","dex_oi":{"xyz":54208596}},{"date":"2025-11-09","dex_oi":{"xyz":59082254}},{"date":"2025-11-10","dex_oi":{"xyz":49966963}},{"date":"2025-11-11","dex_oi":{"xyz":49358546}},{"date":"2025-11-12","dex_oi":{"xyz":52417959}},{"date":"2025-11-13","dex_oi":{"flx":977556,"xyz":56633170,"vntl":88836}},{"date":"2025-11-14","dex_oi":{"xyz":52301218,"vntl":220775,"flx":850618}},{"date":"2025-11-15","dex_oi":{"xyz":55070807,"vntl":333555,"flx":954919}},{"date":"2025-11-16","dex_oi":{"vntl":411827,"xyz":61287113,"flx":1031601}},{"date":"2025-11-17","dex_oi":{"xyz":62734820,"flx":1039801,"vntl":366835}},{"date":"2025-11-18","dex_oi":{"vntl":325668,"xyz":72277208,"flx":1041314}},{"date":"2025-11-19","dex_oi":{"xyz":95917599,"vntl":358599,"flx":1353990}},{"date":"2025-11-20","dex_oi":{"vntl":599139,"xyz":100479901,"flx":1835853}},{"date":"2025-11-21","dex_oi":{"flx":978165,"xyz":92303543,"vntl":618280}},{"date":"2025-11-22","dex_oi":{"vntl":630834,"flx":953665,"xyz":92951015}},{"date":"2025-11-23","dex_oi":{"flx":993161,"vntl":833946,"xyz":95430948}},{"date":"2025-11-24","dex_oi":{"flx":1571680,"xyz":116771643,"vntl":1059308}},{"date":"2025-11-25","dex_oi":{"xyz":132685149,"vntl":1619457,"flx":1900642}},{"date":"2025-11-26","dex_oi":{"vntl":2181103,"flx":3992342,"xyz":149820820}},{"date":"2025-11-27","dex_oi":{"flx":3817927.26,"vntl":2137480.02,"xyz":151339336.57}},{"date":"2025-11-28","dex_oi":{"vntl":2128199.48,"xyz":157143918.21,"flx":4349390.91}},{"date":"2025-11-29","dex_oi":{"xyz":157066953.24,"vntl":2353103.22,"flx":4557220.34}},{"date":"2025-11-30","dex_oi":{"xyz":160662669.16,"vntl":2282374.81,"flx":5091391.33}},{"date":"2025-12-01","dex_oi":{"xyz":154839468.12,"flx":3523682.54,"vntl":2237426.04}},{"date":"2025-12-02","dex_oi":{"vntl":2607444.64,"xyz":156586987.16,"flx":3973328.2}},{"date":"2025-12-03","dex_oi":{"hyna":56.04,"flx":4210757.03,"vntl":2097564.79,"xyz":169432615.2}},{"date":"2025-12-04","dex_oi":{"hyna":83.8,"vntl":2079102.83,"flx":4868535.51,"xyz":184374639.57}},{"date":"2025-12-05","dex_oi":{"vntl":2465621.19,"hyna":447.49,"xyz":183111549.41,"flx":4146656.14}},{"date":"2025-12-06","dex_oi":{"flx":4496695.01,"vntl":2582359.95,"xyz":178945915.42,"hyna":3104.44}},{"date":"2025-12-07","dex_oi":{"vntl":2408797.68,"xyz":182946384.2,"hyna":3324.43,"flx":4449625.3}},{"date":"2025-12-08","dex_oi":{"vntl":2329463.07,"hyna":12608.21,"flx":4591993.54,"xyz":190851109.64}},{"date":"2025-12-09","dex_oi":{"vntl":2398990.16,"hyna":5001819.64,"xyz":172842706.46,"flx":4206674.2}},{"date":"2025-12-10","dex_oi":{"hyna":8436854.28,"flx":4544910.03,"xyz":176016143.5,"vntl":3232138.86}},{"date":"2025-12-11","dex_oi":{"flx":4586806.19,"xyz":169001949.41,"vntl":3223668.06,"hyna":13366151.24}},{"date":"2025-12-12","dex_oi":{"flx":5072891.96,"vntl":3266734.78,"xyz":148546641.09,"hyna":15336194.67}},{"date":"2025-12-13","dex_oi":{"hyna":19649711.89,"xyz":148227704.17,"flx":5401071.03,"vntl":3372669.16}},{"date":"2025-12-14","dex_oi":{"hyna":21171413.37,"xyz":156973588.65,"flx":5434599.6,"vntl":3205843.12}},{"date":"2025-12-15","dex_oi":{"flx":5974637.16,"hyna":21374960.75,"xyz":169865640.88,"vntl":3018557.55}},{"date":"2025-12-16","dex_oi":{"hyna":18674741.43,"xyz":180286752.41,"vntl":3035148.17,"flx":6606833.18}},{"date":"2025-12-17","dex_oi":{"hyna":17767436.36,"vntl":3279923.65,"flx":5970855.51,"xyz":156816278.11}},{"date":"2025-12-18","dex_oi":{"hyna":17783959.68,"vntl":3281011.14,"flx":7294632.03,"xyz":185337503.62}},{"date":"2025-12-19","dex_oi":{"xyz":173302006.38,"hyna":19038335.44,"vntl":3020721.03,"flx":6939140.09}},{"date":"2025-12-20","dex_oi":{"flx":7249828.13,"xyz":172179002.42,"vntl":3068408.2,"hyna":19992435.5}},{"date":"2025-12-21","dex_oi":{"vntl":2657091.73,"flx":7621710.41,"xyz":174767401.16,"hyna":21848190.31}},{"date":"2025-12-22","dex_oi":{"hyna":21662490.36,"vntl":2798961.7,"flx":9412763.44,"km":0,"xyz":191528048.96}},{"date":"2025-12-23","dex_oi":{"km":0,"flx":9591798.05,"vntl":2690122.44,"xyz":207772511.06,"hyna":23729189.05}},{"date":"2025-12-24","dex_oi":{"xyz":206291321.61,"km":0,"hyna":24795200.37,"vntl":2770337.3,"flx":10056488.41}},{"date":"2025-12-25","dex_oi":{"km":0,"xyz":207345620.8,"vntl":2910605.19,"hyna":25895562.21,"flx":10741982.25}},{"date":"2025-12-26","dex_oi":{"km":0,"flx":12763051.33,"vntl":2634993.51,"xyz":214846808.7,"hyna":28149664.76}},{"date":"2025-12-27","dex_oi":{"vntl":3196652.55,"xyz":217015430.22,"km":0,"flx":16022986.05,"hyna":34509343.47}},{"date":"2025-12-28","dex_oi":{"flx":20531277.75,"hyna":35802228.24,"km":0,"vntl":3144358.61,"xyz":223924223.39}},{"date":"2025-12-29","dex_oi":{"vntl":3308510.35,"xyz":211105979.88,"hyna":36244818.42,"km":0,"flx":10092373.36}},{"date":"2025-12-30","dex_oi":{"flx":11396007.58,"hyna":36871211.55,"xyz":219575430.06,"km":0,"vntl":3195395.94}},{"date":"2025-12-31","dex_oi":{"xyz":231307276.71,"km":0,"flx":12659117.29,"hyna":38249664.31,"vntl":2775633.09}},{"date":"2026-01-01","dex_oi":{"xyz":226964349.94,"hyna":40179955.4,"flx":12742730.73,"vntl":2841718.49,"km":0}},{"date":"2026-01-02","dex_oi":{"xyz":221211390.73,"hyna":38114120.6,"vntl":3062045.24,"km":0,"flx":11448749.4}},{"date":"2026-01-03","dex_oi":{"hyna":41161603.99,"flx":12063150.04,"km":0,"vntl":3174078.22,"xyz":221795409.18}},{"date":"2026-01-04","dex_oi":{"xyz":228617683.62,"vntl":2970684.68,"km":0,"flx":12284564.83,"hyna":41926190.74}},{"date":"2026-01-05","dex_oi":{"flx":12746536.49,"xyz":239963386.59,"km":0,"vntl":3183147.67,"hyna":41992024.7}},{"date":"2026-01-06","dex_oi":{"vntl":2987488.91,"xyz":258061695.22,"hyna":41263196.96,"km":0,"flx":15758319.01}},{"date":"2026-01-07","dex_oi":{"km":0,"vntl":3047192.58,"hyna":45318513.68,"xyz":274178876.88,"flx":17175851.64}},{"date":"2026-01-08","dex_oi":{"km":0,"vntl":3707749.73,"flx":15976420.1,"xyz":278543096.93,"hyna":45685790.78}},{"date":"2026-01-09","dex_oi":{"km":0,"xyz":285179916.48,"flx":16306606.95,"vntl":3864833.66,"hyna":46787507.53}},{"date":"2026-01-10","dex_oi":{"xyz":288785441.22,"vntl":3816362.78,"flx":16620848.19,"km":0,"hyna":48973584.27}},{"date":"2026-01-11","dex_oi":{"hyna":49820442.49,"xyz":292805798.63,"vntl":3856784.31,"km":0,"flx":20763878.09}},{"date":"2026-01-12","dex_oi":{"km":4235713.91,"hyna":54066819.43,"vntl":3761025.35,"flx":23950955.86,"xyz":318257981.34}},{"date":"2026-01-13","dex_oi":{"xyz":325601421.96,"km":2613110.68,"hyna":52087839.14,"flx":28178248.58,"abcd":0,"vntl":3848440.47}},{"date":"2026-01-14","dex_oi":{"abcd":0,"km":3617435.64,"xyz":338074376.89,"flx":28815726.59,"vntl":4483750.27,"hyna":47994201.02}},{"date":"2026-01-15","dex_oi":{"vntl":4437580.18,"km":6700248.8,"flx":24854682.4,"hyna":47161694.58,"abcd":0,"xyz":333605505.98}},{"date":"2026-01-16","dex_oi":{"xyz":361629450.12,"km":6902851.77,"vntl":4926876.72,"flx":20747602.71,"hyna":47567028.15,"cash":0,"abcd":0}},{"date":"2026-01-17","dex_oi":{"abcd":0,"hyna":48155658.8,"km":7322539.52,"cash":0,"vntl":5305317.16,"xyz":368987052.81,"flx":19961788.54}},{"date":"2026-01-18","dex_oi":{"abcd":0,"vntl":4581488.49,"hyna":48834268.06,"km":7207283.6,"xyz":383481559.18,"cash":0,"flx":21936939.8}},{"date":"2026-01-19","dex_oi":{"xyz":427195045.52,"km":6685424.71,"hyna":49212068.52,"flx":22757857.7,"cash":0,"vntl":4602878.17,"abcd":0}},{"date":"2026-01-20","dex_oi":{"abcd":0,"km":6137481.53,"vntl":4001716.81,"flx":19290865.03,"cash":357421.57,"xyz":418425509.37,"hyna":45184474.74}},{"date":"2026-01-21","dex_oi":{"cash":551728.23,"hyna":45029961.52,"xyz":439521773.28,"vntl":4222839.56,"km":5418188.86,"abcd":0,"flx":16861996.01}},{"date":"2026-01-22","dex_oi":{"abcd":0,"flx":17502580.18,"xyz":464594975.33,"vntl":3866614.3,"hyna":45698941.73,"km":6906466.07,"cash":907205.43}},{"date":"2026-01-23","dex_oi":{"xyz":539951380.65,"flx":20704375.12,"cash":3347847.56,"vntl":3353346.25,"km":8053520.85,"abcd":0,"hyna":49387150.34}},{"date":"2026-01-24","dex_oi":{"abcd":0,"flx":23550034.23,"xyz":568031926.74,"vntl":3412273.37,"hyna":57053265.45,"km":9081115.31,"cash":10707370}},{"date":"2026-01-25","dex_oi":{"flx":20999633.02,"hyna":58142412.38,"abcd":0,"km":9205830.94,"cash":12421520.45,"vntl":3589178.93,"xyz":658936417.23}},{"date":"2026-01-26","dex_oi":{"hyna":60212825.98,"vntl":3574530.02,"km":9879273.02,"cash":6671328.38,"xyz":650865329.84,"abcd":0,"flx":21338862.59}},{"date":"2026-01-27","dex_oi":{"km":14242778.48,"cash":8501238.2,"xyz":723455264.58,"vntl":3533498.32,"abcd":0,"hyna":64249363.5,"flx":20442482.24}},{"date":"2026-01-28","dex_oi":{"vntl":3875817.75,"xyz":826710224.97,"abcd":0,"hyna":63637665.63,"flx":22366376.03,"km":15462845.75,"cash":14108391.29}},{"date":"2026-01-29","dex_oi":{"cash":24533345.96,"hyna":61678416.99,"flx":24101950.3,"km":16457195.82,"abcd":0,"xyz":923744091.76,"vntl":4718041.61}},{"date":"2026-01-30","dex_oi":{"xyz":739478793.32,"vntl":4943688.72,"km":18568810.15,"abcd":0,"hyna":63267105.04,"cash":13617916.97,"flx":15682661.06}},{"date":"2026-01-31","dex_oi":{"vntl":4584460.93,"abcd":0,"cash":17284554.14,"xyz":697412339.2,"flx":14158849.49,"km":18648503.53,"hyna":53933769.03}},{"date":"2026-02-01","dex_oi":{"hyna":52734611.31,"km":20963345.49,"flx":12509536.04,"vntl":5282610.91,"cash":43319949.49,"abcd":0,"xyz":705103209.74}},{"date":"2026-02-02","dex_oi":{"xyz":775411792.64,"vntl":5137488.43,"flx":11329396.29,"hyna":52624907.13,"cash":19787584.91,"km":18102859.04,"abcd":0}},{"date":"2026-02-03","dex_oi":{"hyna":48602800.25,"abcd":0,"xyz":688182219.49,"cash":25898968.69,"km":19228031.74,"vntl":6159103.26,"flx":14654975.57}},{"date":"2026-02-04","dex_oi":{"flx":16066159.45,"cash":27883502.59,"abcd":0,"xyz":632897380.28,"hyna":51799388.08,"km":19355337.81,"vntl":6369890.9}},{"date":"2026-02-05","dex_oi":{"flx":12167785,"vntl":6646582.42,"hyna":40079710.12,"cash":28376204.32,"km":16216672.16,"xyz":519836360.95,"abcd":0}},{"date":"2026-02-06","dex_oi":{"flx":13348165.14,"km":18129519.04,"vntl":6450255.04,"abcd":0,"cash":26699344.78,"xyz":516991089.12,"hyna":42701477.44}},{"date":"2026-02-07","dex_oi":{"cash":26282514.2,"km":19062089.31,"flx":13573874.57,"xyz":528319359.21,"abcd":0,"vntl":6524828.89,"hyna":43470470.01}},{"date":"2026-02-08","dex_oi":{"hyna":43721687.89,"xyz":552406222.43,"km":18450666.72,"cash":28256394.96,"vntl":6640530.39,"abcd":0,"flx":15477162.41}},{"date":"2026-02-09","dex_oi":{"flx":9724079.3,"km":14905551.42,"vntl":7455770.56,"xyz":637670832.99,"hyna":43904969.64,"abcd":0,"cash":35239707.5}},{"date":"2026-02-10","dex_oi":{"xyz":620852593.11,"flx":10800273.78,"cash":28669391.6,"km":15688887.04,"abcd":0,"vntl":7097267.35,"hyna":42928565.83}},{"date":"2026-02-11","dex_oi":{"abcd":0,"xyz":646831187.66,"km":15920425.19,"vntl":6286573.49,"hyna":40982832.65,"cash":29303553.76,"flx":10128285.09}},{"date":"2026-02-12","dex_oi":{"cash":28664713.46,"flx":9970526.15,"xyz":599487756.36,"abcd":0,"hyna":43299541.61,"vntl":6407029.76,"km":18278984.8}},{"date":"2026-02-13","dex_oi":{"vntl":6516760.88,"km":17738554.02,"xyz":595745690.96,"cash":29823260.1,"flx":9430184.72,"hyna":43362771.18,"abcd":0}},{"date":"2026-02-14","dex_oi":{"km":19024250.93,"cash":31242430.03,"flx":9402472.17,"vntl":6729734.04,"xyz":589527251.87,"abcd":0,"hyna":44368315.27}},{"date":"2026-02-15","dex_oi":{"hyna":43330589.37,"xyz":612408201.22,"vntl":6470602.08,"cash":37349872.74,"km":19396550.64,"flx":10711977.34,"abcd":0}},{"date":"2026-02-16","dex_oi":{"km":19399728.08,"xyz":608066325.4,"abcd":0,"flx":9763856.51,"hyna":44476962.29,"cash":33086976.57,"vntl":6426370.37}},{"date":"2026-02-17","dex_oi":{"hyna":43067409.5,"abcd":0,"xyz":606221347.63,"vntl":6768325.72,"km":15850606.09,"cash":35176588.86,"flx":10468394.88}},{"date":"2026-02-18","dex_oi":{"hyna":42089864.37,"cash":40709700.4,"xyz":672010389.11,"flx":12231627,"abcd":0,"km":17823240.66,"vntl":6829825.44}},{"date":"2026-02-19","dex_oi":{"flx":13075454.01,"km":17600178.12,"cash":44465656.92,"abcd":0,"hyna":42945480.99,"xyz":684538626.68,"vntl":7982086.67}},{"date":"2026-02-20","dex_oi":{"xyz":713652026.2,"abcd":0,"hyna":44928756.62,"flx":11912717.11,"km":18171213.73,"cash":48490766.81,"vntl":8096688.95}},{"date":"2026-02-21","dex_oi":{"flx":12099170.01,"vntl":8433052.95,"hyna":45542029.26,"abcd":0,"km":20601202.15,"xyz":717188790.58,"cash":45898588.93}},{"date":"2026-02-22","dex_oi":{"xyz":758733012.77,"flx":12545409.1,"hyna":47020813.87,"vntl":8425183.63,"cash":49289901.69,"km":22735411.83,"abcd":0}},{"date":"2026-02-23","dex_oi":{"abcd":0,"hyna":44591239.08,"cash":46901850.84,"km":18856582.76,"xyz":756764776.6,"vntl":7685065.81,"flx":11150748.81}},{"date":"2026-02-24","dex_oi":{"abcd":0,"flx":10776700.37,"hyna":45474605.55,"xyz":764004747.68,"cash":50233165.06,"km":18340076.36,"vntl":7534349.84}},{"date":"2026-02-25","dex_oi":{"abcd":0,"flx":11663797.78,"km":18471293.64,"hyna":45745895.97,"cash":49977378,"vntl":7904670.18,"xyz":780048923.51}},{"date":"2026-02-26","dex_oi":{"abcd":0,"hyna":45815069.36,"vntl":7570102.05,"flx":10444060.36,"xyz":800800773.13,"km":16980766.53,"cash":44915349.6}},{"date":"2026-02-27","dex_oi":{"cash":63959573.77,"abcd":0,"hyna":44007762.4,"xyz":865983014.99,"flx":14779241.53,"km":18102637.12,"vntl":8777346.95}},{"date":"2026-02-28","dex_oi":{"xyz":942016926.07,"cash":60528244.45,"hyna":43100898.39,"flx":16620561.3,"km":25317142.94,"vntl":11956319.69,"abcd":0}},{"date":"2026-03-01","dex_oi":{"flx":18313066.81,"abcd":0,"hyna":42266555.54,"km":25910339.91,"cash":53819010.75,"vntl":13574986.35,"xyz":975391502.68}},{"date":"2026-03-02","dex_oi":{"hyna":44661780.18,"xyz":897884115.48,"abcd":0,"km":21402167.93,"cash":47916253.97,"flx":15501540.49,"vntl":11660290.82}},{"date":"2026-03-03","dex_oi":{"hyna":43676303.28,"xyz":804232871.49,"flx":15496679.09,"abcd":0,"vntl":9802151.46,"km":18223814.37,"cash":62312849.81}},{"date":"2026-03-04","dex_oi":{"cash":61954518.65,"hyna":45667316.66,"flx":15829816.25,"vntl":10162354.37,"km":17569683.33,"xyz":791619051.37,"abcd":0}},{"date":"2026-03-05","dex_oi":{"abcd":0,"km":15896083.07,"hyna":44865173.34,"cash":58156645.6,"vntl":10293671.18,"flx":15969448.44,"xyz":820166464.43}}]""")

# ── Parse (exclude XYZ and abcd) ──
deployers = ['flx', 'vntl', 'hyna', 'km', 'cash']
records = []
for entry in raw:
    row = {'date': entry['date']}
    dex = entry.get('dex_oi', {})
    for key in deployers:
        row[key] = dex.get(key, 0)
    records.append(row)

df = pd.DataFrame(records)
df['date'] = pd.to_datetime(df['date'])

# ── Weekly: use end-of-week (Sunday) snapshot as OI value ──
# OI is a snapshot metric, so we take the last day of each week
df['week'] = df['date'].dt.to_period('W-SUN').apply(lambda r: r.start_time)
# Take last observation per week (= end-of-week snapshot)
weekly = df.groupby('week')[deployers].last().reset_index()

# Filter from 11/24/2025 (when non-XYZ deployers appear)
weekly = weekly[weekly['week'] >= '2025-11-10'].copy()

# ── Colors (matching deployers weekly volume chart) ──
labels = ['Felix', 'VNTL', 'HYNA', 'KM', 'Cash']
colors = ['#1a3a5c', '#5b8fb9', '#1b2a4a', '#9cc5a1', '#a8c8d8']

# ── Plot ──
fig, ax = plt.subplots(figsize=(10.67, 4.67), dpi=150)
fig.patch.set_alpha(0)
ax.set_facecolor('none')

bar_width = 5.0
bottoms = np.zeros(len(weekly))

for i, (dep, label, color) in enumerate(zip(deployers, labels, colors)):
    values = weekly[dep].values / 1e6  # millions
    ax.bar(
        weekly['week'],
        values,
        bottom=bottoms,
        width=bar_width,
        color=color,
        label=label,
        edgecolor='#0a0a0a',
        linewidth=0.3,
        alpha=0.92,
    )
    bottoms += values

# ── Y axis (unified $M) ──
max_val = bottoms.max()
y_max = np.ceil(max_val / 50) * 50
ticks = np.linspace(0, y_max, 5)
ax.set_ylim(0, y_max * 1.08)
ax.yaxis.set_major_locator(mticker.FixedLocator(ticks))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
for label in ax.get_yticklabels():
    label.set_fontproperties(font_bold)
    label.set_fontsize(14)
    label.set_color('#747474')

# ── X axis (MM/DD/YYYY matching volume chart) ──
ax.set_xlim(weekly['week'].min() - pd.Timedelta(days=4), weekly['week'].max() + pd.Timedelta(days=6))
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d/%Y'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
         fontproperties=font_bold, fontsize=12, color='#747474')

# ── Grid ──
ax.grid(axis='y', color='#787b86', alpha=0.5, linestyle=(0, (3.7, 1.6)), linewidth=1)
ax.grid(axis='x', visible=False)
ax.set_axisbelow(True)

# ── Spines ──
for spine in ax.spines.values():
    spine.set_visible(False)

# ── Tick params ──
ax.tick_params(axis='x', length=6, width=1, color='#747474')
ax.tick_params(axis='y', length=0)

fig.tight_layout()

# ── Save ──
out_dir = Path('/Users/ijaheun/Desktop/Project/data/outputs/charts/hip3')
png_path = out_dir / 'hip3_deployers_weekly_oi.png'
svg_path = out_dir / 'hip3_deployers_weekly_oi.svg'

fig.savefig(png_path, dpi=150, bbox_inches='tight', transparent=True)
fig.savefig(svg_path, format='svg', bbox_inches='tight', transparent=True)
plt.close(fig)

print(f"Saved: {png_path}")
print(f"Saved: {svg_path}")

print(f"\nWeekly OI excl. XYZ ({len(weekly)} weeks):")
for _, row in weekly.iterrows():
    total = sum(row[d] for d in deployers) / 1e6
    print(f"  {row['week'].strftime('%m/%d/%Y')}: ${total:.0f}M")
