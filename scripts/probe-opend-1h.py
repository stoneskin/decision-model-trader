"""Probe: OpenD 能拉回几个月的 1 小时 K 线？在装 OpenD 的那台机器上跑。

用法：pip install moomoo-api
     python probe-opend-1h.py
要求：OpenD 已登录、在本机 127.0.0.1:11111 监听。
输出：每只标的拉回的 bar 数 + 起止时间。
"""

from moomoo import AuType, KL_FIELD, KLType, OpenQuoteContext, RET_OK

SYMBOLS = ["US.QQQ", "US.TQQQ", "US.SQQQ"]


def main():
    ctx = OpenQuoteContext(host="127.0.0.1", port=11111)
    for sym in SYMBOLS:
        ret, data = ctx.request_history_kline(
            sym,
            start="2026-05-26",
            end="2026-11-23",
            ktype=KLType.K_60M,
            autype=AuType.QFQ,
            fields=[KL_FIELD.ALL],
            max_count=1000,
        )
        if ret != RET_OK:
            print(sym, "失败:", data)
            continue
        print(
            sym,
            "bars:",
            len(data),
            "from",
            data["time_key"].iloc[0],
            "to",
            data["time_key"].iloc[-1],
        )
    ctx.close()


if __name__ == "__main__":
    main()
