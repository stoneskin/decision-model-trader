# decision-model-trader

小时级模拟盘实验：本地小模型每小时筛查 QQQ / TQQQ / SQQQ 的涨跌概率，
低置信度升级 OpenRouter 大模型复核；先离线回测，再接 moomoo OpenD 模拟盘。

> 状态（2026-11-23）：搭架子阶段，只有文档，没有交易代码。回测未跑，未接 OpenD。

## 架构：轻管线

```
1h K 线（moomoo / yfinance）
  → 特征（动量 / 波动 / 成交量，按小时重定义）
  → 本地小模型筛查，输出 P(涨) + 校准
  → 置信度低 → OpenRouter 大模型复核（只复核，不常规调用）
  → 信号 → 仓位规则 → 离线 walk-forward 回测
  → 纸交易：moomoo-api + OpenD，硬编码 TrdEnv.SIMULATE
  → 每次决策存特征 / 概率 / 复核记录（供 thinktank 离线审计）
```

- 本地小模型首选候选：Strands Decider 2B（开源权重，Apache-2.0）；Jev 可作同层候选或对照组。
- thinktank 不进热循环，只作离线审计（每日收盘后复核管线决策）与疑难升级。
- 调研结论（2026-11-23）：没有现成开源项目能直接用，qlib 也没有这个功能，所以自建轻管线。

## 护栏（硬约束）

- 全新套路，不受现行实盘纪律约束；实盘纪律不动。
- 不碰实盘。将来任何涉及下单的代码必须硬编码 `SIMULATE`，不得以参数默认值或配置项绕开。
- 模拟盘每单显式传 `SIMULATE`。
- 不建定时任务（agent 跑在台式机上，不是 Muse 这边的 cron）。

## 文件

| 文件 | 内容 |
|---|---|
| `BRIEF.md` | 已定简报全文：目标、形态、标的、架构、两步走、实验期与考核（含三处待 Stone 确认的默认项） |
| `BACKTEST-PLAN.md` | 离线回测计划：数据、特征、模型臂、校准、升级规则、walk-forward 评估 |
| `README.md` | 本文件 |
| `.gitignore` | Python / venv / data / .env |

## 下一步

1. Stone 在台式机 clone 本仓库，审 `BRIEF.md` 与 `BACKTEST-PLAN.md`。
2. 确认 `BRIEF.md` 里的三处默认项（OpenD 位置、实验期与考核、显卡型号）。
3. 在台式机上实测 Strands Decider 2B 能否跑起来（见 `BRIEF.md` 的核验节；注意官方文档说 Windows 下走 WSL2）。
4. 按 `BACKTEST-PLAN.md` 跑离线回测；回测通过后再接 OpenD 模拟盘。
