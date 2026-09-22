"""
HIP-3 S3 Data Extractor
- S3 node_fills_by_block에서 HIP-3 체결 데이터 추출
- 날짜별 CSV + 일별 통계 CSV 생성

Volume: Buy side fills의 px * sz 합산
Trades: Buy side 고유 tid 카운트
OI: Open(B:Open Long + A:Open Short + flip open) - Close(A:Close Long + B:Close Short + flip close + liquidation) 누적
"""

import json, os, csv, sys, subprocess
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# 설정
OUTPUT_DIR = "/Users/ijaheun/Desktop/Project/data/outputs/data/hip3"
TMP_DIR = "/tmp/hip3_extract"
S3_BUCKET = "s3://hl-mainnet-node-data/node_fills_by_block/hourly"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/daily", exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


def download_day(date_str):
    """S3에서 하루치 lz4 다운로드 (병렬)"""
    day_dir = f"{TMP_DIR}/{date_str}"
    os.makedirs(day_dir, exist_ok=True)

    procs = []
    for hour in range(24):
        lz4_path = f"{day_dir}/{hour}.lz4"
        if os.path.exists(lz4_path):
            continue
        cmd = f"aws s3 cp {S3_BUCKET}/{date_str}/{hour}.lz4 {lz4_path} --request-payer requester"
        procs.append(subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

    for p in procs:
        p.wait()

    return day_dir


def process_day(day_dir, target_date):
    """하루치 데이터에서 HIP-3 fills 추출 + 통계 계산"""
    fills = []
    stats = {
        "date": target_date,
        "volume": 0,
        "trades": set(),
        "open_vol": 0,
        "close_vol": 0,
        # deployer별
        "deployer_volume": defaultdict(float),
        "deployer_trades": defaultdict(set),
        "deployer_open": defaultdict(float),
        "deployer_close": defaultdict(float),
        # dir별 카운트
        "dir_counts": defaultdict(int),
    }

    for hour in range(24):
        lz4_path = f"{day_dir}/{hour}.lz4"
        json_path = f"{day_dir}/{hour}.json"
        if not os.path.exists(lz4_path):
            continue

        os.system(f"unlz4 -f {lz4_path} {json_path} 2>/dev/null")
        if not os.path.exists(json_path):
            continue

        with open(json_path) as f:
            for line in f:
                try:
                    row = json.loads(line)
                    for event in row.get("events", []):
                        if len(event) < 2:
                            continue
                        fill = event[1]
                        coin = fill.get("coin", "")
                        if ":" not in coin:
                            continue

                        t = datetime.fromtimestamp(fill["time"] / 1000, tz=timezone.utc)
                        if t.strftime("%Y-%m-%d") != target_date:
                            continue

                        side = fill.get("side", "")
                        dir_val = fill.get("dir", "")
                        px = float(fill.get("px", 0))
                        sz = float(fill.get("sz", 0))
                        vol = px * sz
                        deployer = coin.split(":")[0]
                        ticker = coin.split(":")[1]
                        tid = fill.get("tid")

                        # CSV용 fill 저장
                        fills.append({
                            "datetime_utc": t.strftime("%Y-%m-%d %H:%M:%S"),
                            "deployer": deployer,
                            "ticker": ticker,
                            "side": side,
                            "dir": dir_val,
                            "px": fill.get("px"),
                            "sz": fill.get("sz"),
                            "volume_usd": round(vol, 2),
                            "fee": fill.get("fee", ""),
                            "deployerFee": fill.get("deployerFee", ""),
                            "closedPnl": fill.get("closedPnl", ""),
                            "tid": tid,
                            "crossed": fill.get("crossed", ""),
                            "builder": fill.get("builder", ""),
                            "feeToken": fill.get("feeToken", ""),
                        })

                        # Volume & Trades (Buy side only)
                        if side == "B":
                            stats["volume"] += vol
                            stats["trades"].add(tid)
                            stats["deployer_volume"][deployer] += vol
                            stats["deployer_trades"][deployer].add(tid)

                        # Dir 카운트
                        stats["dir_counts"][f"{side}:{dir_val}"] += 1

                        # OI 계산
                        if side == "B" and dir_val == "Open Long":
                            stats["open_vol"] += vol
                            stats["deployer_open"][deployer] += vol
                        elif side == "A" and dir_val == "Open Short":
                            stats["open_vol"] += vol
                            stats["deployer_open"][deployer] += vol
                        elif side == "A" and dir_val == "Close Long":
                            stats["close_vol"] += vol
                            stats["deployer_close"][deployer] += vol
                        elif side == "B" and dir_val == "Close Short":
                            stats["close_vol"] += vol
                            stats["deployer_close"][deployer] += vol
                        elif side == "B" and dir_val == "Short > Long":
                            stats["open_vol"] += vol
                            stats["close_vol"] += vol
                            stats["deployer_open"][deployer] += vol
                            stats["deployer_close"][deployer] += vol
                        elif side == "A" and dir_val == "Long > Short":
                            stats["open_vol"] += vol
                            stats["close_vol"] += vol
                            stats["deployer_open"][deployer] += vol
                            stats["deployer_close"][deployer] += vol
                        elif "Liquidat" in dir_val or "Auto-Deleverag" in dir_val:
                            stats["close_vol"] += vol
                            stats["deployer_close"][deployer] += vol

                except Exception:
                    pass

        os.remove(json_path)

    return fills, stats


def save_daily_csv(fills, date_str):
    """날짜별 raw fills CSV 저장"""
    if not fills:
        return None

    path = f"{OUTPUT_DIR}/daily/hip3_fills_{date_str.replace('-', '')}.csv"
    fieldnames = ["datetime_utc", "deployer", "ticker", "side", "dir", "px", "sz",
                  "volume_usd", "fee", "deployerFee", "closedPnl", "tid", "crossed",
                  "builder", "feeToken"]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fills)

    size_mb = os.path.getsize(path) / 1024 / 1024
    return path, size_mb


def main(start_date, end_date):
    all_daily_stats = []
    cumulative_oi = 0
    deployer_cum_oi = defaultdict(float)

    current = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        s3_date = current.strftime("%Y%m%d")

        print(f"\n{'='*60}")
        print(f"처리 중: {date_str}")

        # 1. 다운로드
        print(f"  S3 다운로드...")
        day_dir = download_day(s3_date)

        # 2. 추출 + 통계
        print(f"  데이터 추출...")
        fills, stats = process_day(day_dir, date_str)

        # 3. 날짜별 CSV 저장
        if fills:
            path, size_mb = save_daily_csv(fills, date_str)
            print(f"  CSV 저장: {path} ({size_mb:.1f} MB, {len(fills):,}건)")
        else:
            print(f"  HIP-3 데이터 없음")

        # 4. OI 누적
        net_oi = stats["open_vol"] - stats["close_vol"]
        cumulative_oi += net_oi

        for dep in set(list(stats["deployer_open"].keys()) + list(stats["deployer_close"].keys())):
            dep_net = stats["deployer_open"][dep] - stats["deployer_close"][dep]
            deployer_cum_oi[dep] += dep_net

        # 5. 통계 기록
        deployers = sorted(set(
            list(stats["deployer_volume"].keys()) +
            list(stats["deployer_open"].keys())
        ))

        row = {
            "date": date_str,
            "total_volume": round(stats["volume"], 2),
            "total_trades": len(stats["trades"]),
            "total_fills": len(fills),
            "open_vol": round(stats["open_vol"], 2),
            "close_vol": round(stats["close_vol"], 2),
            "net_oi_change": round(net_oi, 2),
            "cumulative_oi": round(cumulative_oi, 2),
        }

        # deployer별 컬럼 추가
        for dep in ["xyz", "cash", "flx", "hyna", "km", "vntl"]:
            row[f"{dep}_volume"] = round(stats["deployer_volume"].get(dep, 0), 2)
            row[f"{dep}_trades"] = len(stats["deployer_trades"].get(dep, set()))
            row[f"{dep}_oi"] = round(deployer_cum_oi.get(dep, 0), 2)

        all_daily_stats.append(row)

        print(f"  Volume: ${stats['volume']:,.0f}")
        print(f"  Trades: {len(stats['trades']):,}")
        print(f"  OI Change: ${net_oi:+,.0f}")
        print(f"  Cumulative OI: ${cumulative_oi:,.0f}")

        current += timedelta(days=1)

    # 6. 일별 통계 CSV 저장
    summary_path = f"{OUTPUT_DIR}/hip3_daily_summary_{start_date.replace('-','')}_to_{end_date.replace('-','')}.csv"
    if all_daily_stats:
        fieldnames = list(all_daily_stats[0].keys())
        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_daily_stats)
        print(f"\n{'='*60}")
        print(f"일별 통계 저장: {summary_path}")

    # 7. tmp 정리
    print(f"\ntmp 정리 중...")
    os.system(f"rm -rf {TMP_DIR}")
    print("완료!")


if __name__ == "__main__":
    start = sys.argv[1] if len(sys.argv) > 1 else "2025-10-12"
    end = sys.argv[2] if len(sys.argv) > 2 else "2025-10-31"
    main(start, end)
