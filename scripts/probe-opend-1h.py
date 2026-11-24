"""Probe: OpenD 能拉回几个月的 1 小时 K 线？在装 OpenD 的那台机器上跑。

用法：
  pip install moomoo-api
  python probe-opend-1h.py [--host 127.0.0.1] [--port 11111]
      [--rsa-key C:\\path\\to\\rsa_private_key_pkcs1.pem]

说明：
- OpenD 配了 RSA（OpenD.xml 里有 rsa_private_key）时，必须带密钥加密连接，
  否则握手报 check sha error。密钥路径用 --rsa-key 传，或设环境变量
  MOOMOO_RSA_KEY。密钥文件本身绝不进库（.gitignore 已有 *.pem/*.key）。
- 远程连另一台机器上的 OpenD 时用 --host 指定地址（OpenD 须监听 0.0.0.0）。
- 输出：每只标的拉回的 bar 数 + 起止时间。
"""

import argparse
import os

from moomoo import (
    AuType,
    KL_FIELD,
    KLType,
    OpenQuoteContext,
    RET_OK,
    SysConfig,
)

SYMBOLS = ["US.QQQ", "US.TQQQ", "US.SQQQ"]


def main():
    ap = argparse.ArgumentParser(description="Probe OpenD 1h history coverage.")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=11111)
    ap.add_argument("--rsa-key", default=os.environ.get("MOOMOO_RSA_KEY"),
                    help="RSA 私钥文件路径（OpenD 配了 rsa_private_key 时必填）")
    args = ap.parse_args()

    if args.rsa_key:
        SysConfig.enable_proto_encrypt(True)
        SysConfig.set_init_rsa_file(args.rsa_key)

    ctx = OpenQuoteContext(host=args.host, port=args.port)
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
