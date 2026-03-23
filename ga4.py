import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
GA4 データ取得モジュール。
Claude Code からこのスクリプトを呼び出してデータを取得する。
使い方: python ga4.py <サイト名> <指標タイプ> [開始日] [終了日]

指標タイプ:
  overview    - PV・セッション・ユーザー数
  channel     - チャネル別セッション
  pages       - ページ別PV
  conversion  - コンバージョン・購入率
  mobile_organic - モバイル×オーガニック購入率

例:
  python ga4.py しまむら overview 30daysAgo today
  python ga4.py アンククロス channel 2024-01-01 2024-01-31
"""

import json
import sys
import os
from auth import authenticate, find_account, load_accounts
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest, DateRange, Metric, Dimension,
    FilterExpression, FilterExpressionList, Filter,
    OrderBy,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_client(account):
    creds = authenticate(account)
    return BetaAnalyticsDataClient(credentials=creds)


def find_property(site_name):
    accounts = load_accounts()
    for acc in accounts:
        for prop in acc["properties"]:
            if site_name in prop["name"] or site_name == prop["id"]:
                return acc, prop
    return None, None


def format_rows(response, dim_names, met_names):
    results = []
    for row in response.rows:
        record = {}
        for i, dim in enumerate(dim_names):
            record[dim] = row.dimension_values[i].value
        for i, met in enumerate(met_names):
            record[met] = row.metric_values[i].value
        results.append(record)
    return results


def run_overview(client, property_id, start_date, end_date):
    """PV・セッション・ユーザー推移"""
    resp = client.run_report(RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="date")],
        metrics=[
            Metric(name="screenPageViews"),
            Metric(name="sessions"),
            Metric(name="activeUsers"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name="date"))],
    ))
    rows = format_rows(resp, ["日付"], ["PV", "セッション", "ユーザー"])
    total_pv = sum(int(r["PV"]) for r in rows)
    total_sessions = sum(int(r["セッション"]) for r in rows)
    total_users = sum(int(r["ユーザー"]) for r in rows)
    print(f"【概要】{start_date} 〜 {end_date}")
    print(f"  PV合計:       {total_pv:,}")
    print(f"  セッション合計: {total_sessions:,}")
    print(f"  ユーザー合計:  {total_users:,}")
    print(f"\n【日別推移】")
    for r in rows:
        print(f"  {r['日付']}  PV:{int(r['PV']):>6,}  セッション:{int(r['セッション']):>6,}  ユーザー:{int(r['ユーザー']):>6,}")


def run_channel(client, property_id, start_date, end_date):
    """チャネル別セッション"""
    resp = client.run_report(RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[
            Metric(name="sessions"),
            Metric(name="activeUsers"),
            Metric(name="bounceRate"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
    ))
    rows = format_rows(resp, ["チャネル"], ["セッション", "ユーザー", "直帰率"])
    print(f"【チャネル別セッション】{start_date} 〜 {end_date}")
    for r in rows:
        print(f"  {r['チャネル']:<30} セッション:{int(r['セッション']):>7,}  直帰率:{float(r['直帰率'])*100:.1f}%")


def run_pages(client, property_id, start_date, end_date):
    """ページ別PV Top20"""
    resp = client.run_report(RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="pagePath"), Dimension(name="pageTitle")],
        metrics=[Metric(name="screenPageViews"), Metric(name="averageSessionDuration")],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="screenPageViews"), desc=True)],
        limit=20,
    ))
    rows = format_rows(resp, ["パス", "タイトル"], ["PV", "平均滞在時間(秒)"])
    print(f"【ページ別PV Top20】{start_date} 〜 {end_date}")
    for i, r in enumerate(rows, 1):
        print(f"  {i:>2}. {int(r['PV']):>6,}PV  {r['パス']}")


def run_mobile_organic(client, property_id, start_date, end_date):
    """モバイル×オーガニック検索の購入率"""
    resp = client.run_report(RunReportRequest(
        property=f"properties/{property_id}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="transactions"),
            Metric(name="purchaseRevenue"),
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        dimension_filter=FilterExpression(
            and_group=FilterExpressionList(expressions=[
                FilterExpression(filter=Filter(
                    field_name="deviceCategory",
                    string_filter=Filter.StringFilter(value="mobile")
                )),
                FilterExpression(filter=Filter(
                    field_name="sessionDefaultChannelGroup",
                    string_filter=Filter.StringFilter(value="Organic Search")
                )),
            ])
        ),
    ))
    if not resp.rows:
        print("データなし（購入計測が未設定の可能性があります）")
        return
    r = resp.rows[0]
    sessions = int(r.metric_values[0].value)
    transactions = int(r.metric_values[1].value)
    revenue = float(r.metric_values[2].value)
    rate = transactions / sessions * 100 if sessions > 0 else 0
    print(f"【モバイル×オーガニック検索】{start_date} 〜 {end_date}")
    print(f"  セッション: {sessions:,}")
    print(f"  購入数:     {transactions:,}")
    print(f"  購入率:     {rate:.2f}%")
    print(f"  売上:       ¥{revenue:,.0f}")


REPORT_TYPES = {
    "overview": run_overview,
    "channel": run_channel,
    "pages": run_pages,
    "mobile_organic": run_mobile_organic,
}

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python ga4.py <サイト名> <指標タイプ> [開始日] [終了日]")
        print("指標タイプ:", ", ".join(REPORT_TYPES.keys()))
        sys.exit(1)

    site_name = sys.argv[1]
    report_type = sys.argv[2]
    start_date = sys.argv[3] if len(sys.argv) > 3 else "30daysAgo"
    end_date = sys.argv[4] if len(sys.argv) > 4 else "today"

    account, prop = find_property(site_name)
    if not account:
        print(f"サイトが見つかりません: {site_name}")
        sys.exit(1)

    if report_type not in REPORT_TYPES:
        print(f"不明な指標タイプ: {report_type}")
        sys.exit(1)

    print(f"サイト: {prop['name']} (ID: {prop['id']})\n")
    client = get_client(account)
    REPORT_TYPES[report_type](client, prop["id"], start_date, end_date)
