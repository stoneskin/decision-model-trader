# BRIEF.md — 决策模型交易（DMT）实验简报

版本：2026-11-23 v1（初稿，待 Stone 审）。已定内容不复议；文末三处默认项待 Stone 确认。

## 1. 目标

验证 Jev 这类小模型在 1 小时频率上预测 QQQ、TQQQ、SQQQ 涨跌概率，
能不能赚钱、动作是不是比日线纪律多且有效。

## 2. 形态

- 新 project，全新套路，不受现行实盘纪律约束，实盘纪律不动。
- agent + 小模型跑在 Stone 台式机上，不是我（Muse）这边的定时任务。
- 实验，不做实盘；模拟盘走 moomoo OpenD，每单显式传 `SIMULATE`。

## 3. 标的

QQQ、TQQQ、SQQQ。

## 4. 架构：轻管线

本地小模型每小时筛查，输出涨跌概率；低置信度升级 OpenRouter 大模型复核；
Jev 可作小模型层候选或对照组；thinktank 不进热循环，只作离线审计
（每日收盘后复核管线决策）与疑难升级。

拓扑（2026-11-23 定）：本地模型服务跑在台式机上（WSL2，HTTP 服务），DMT 代码经本地地址（127.0.0.1:8099）调用模型。OpenD 配了 RSA（OpenD.xml 里 rsa_private_key），DMT 代码须带密钥加密连接（SysConfig.enable_proto_encrypt + set_init_rsa_file），密钥路径按机器配、不进库。

```
1h K 线 → 特征 → 本地小模型 P(涨) → 置信度低 → OpenRouter 大模型复核
→ 信号 → 仓位 → 回测 / 纸交易（SIMULATE）
```

## 5. 两步走

1. **离线回测**：历史 1 小时 K 线，测概率校准 + 阈值策略 vs buy-and-hold QQQ。
   不碰 OpenD、不下单。详见 `BACKTEST-PLAN.md`。
2. **接 OpenD 模拟盘**：回测通过后再接，每单显式传 `SIMULATE`。

## 6. 实验期与考核（默认，待确认，见第 8 节第 ② 项）

- 回测先行，模拟盘跑 4 周。
- 考核三条：概率校准（Brier / log loss）、阈值策略对 buy-and-hold QQQ 的超额收益、
  动作数和胜率。
- 模拟盘仓位：每次信号满仓一只标的（固定名义本金，收益按百分比计；不引入格子制，2026-11-23 清理决定）。

## 7. 本地模型候选核验（2026-11-23 检索）

首选候选：**Strands Decider 2B**（AWS Strands Labs，2026-10-01 发布，Apache-2.0）。

核实到的事实（来源：官方 README 与官方文档站 strandsagents.dev，另有二手写作为佐证）：

- 结构：Qwen3.5-2B torso（共 1.9B 参数），去掉语言模型头，换成约 1M 参数的
  pointer head + rank-16 LoRA；回答三类问题：noul（P(true)）、choice、score。
- 权重与代码：权重在 Hugging Face（`StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`），
  代码在 GitHub（`strands-labs/strands-decider`），`pip install strands-decider`，
  可跑成本地 HTTP 服务（`POST /v1/systemone`）。
- 体积：checkpoint（adapter + head + tokenizer）约 88 MB；base 权重首次运行时从
  Hugging Face 另行下载，约 4.5 GB（二手来源）；Ollama MLX 构建 BF16 约 3.8 GB、
  NVFP4 约 1.3 GB（二手来源）。
- 显存结论：1.9B 参数 BF16 权重约 3.8 GB，加上 4K 上下文的 KV 缓存与开销，
  **16GB 显存绰绰有余**（12GB 也够用）。同系列 Gemma 4 E4B 约 20 GB 显存占用，
  16GB 也装不下；E2B 约 9 GB（BF16），16GB 够，须在台式机实测。
- 延迟：厂商称 RTX 3090 上中位数约 115 ms/问（厂商数据，未独立验证）。
- 上下文窗口：4,096 tokens——每小时输入的状态必须装得进 4K。
- 校准：官方 README 称，未见过的短分类任务上，置信度 ≥0.9 的回答约 95% 正确
  （厂商数据，市场数据上的校准一律以本实验回测实测为准）。
- **Windows 部署注意**：官方推理文档说，服务跑在 Linux 或 Windows 下的 WSL2
  （带 NVIDIA GPU），WSL 内的服务可从 Windows 经 127.0.0.1:8099 访问。
  台式机上部署时须按这条走，不是原生 Windows 服务。
- 未核实：权重未下载、未在台式机上实际跑过；以上“够用”结论是按参数量与
  公开体积数字算的，台式机实测为准。

对照组：Jev（TypeSafe，OpenRouter `typesafe/jev-1.14`，decisions 端点）可作
小模型层候选或对照组；传统分类器（LightGBM 二分类）作基线，见 `BACKTEST-PLAN.md`。

## 8. 待 Stone 确认的默认项

以下按默认写进简报，Stone 没纠正就按默认执行；纠正一条改一条。③ 显卡已于 2026-11-23 确认，剩下两处待确认。

### ① OpenD 在哪台机器上，agent 从哪连（默认）

OpenD 在常开机的笔记本上（Tailscale 上那台 MSI），台式机是另一台；
agent 装台式机上、经 Tailscale 连笔记本的 11111。
（2026-11-23 确认：台式机上跑探针，127.0.0.1:11111 拒绝连接，OpenD 确不在台式机上；DMT 经 Tailscale 连笔记本 11111，OpenD 远程连接待验。另：OpenD.xml 里 ip 是 0.0.0.0，全网卡监听，远程连得通；但 OpenD 配了 RSA，远程连也须带密钥加密。）

### ② 实验期与考核（默认）

回测先行，模拟盘跑 4 周；考核看校准、相对 buy-and-hold QQQ 的超额、
动作数和胜率；模拟盘仓位每次信号满仓一只标的（固定名义本金，不引入格子制）。

### ③ 显卡型号（已确认 2026-11-23）

RTX 5070 Ti 16GB。之前记录的 RTX 5070 12GB 是错的，已更正。

## 9. 调研结论（2026-11-23）

没有现成开源项目能直接用（qlib 也没有这个功能：无 LLM/小决策模型、
无小时模式、无实盘循环、无 moomoo 执行），所以自建轻管线；
qlib 只适合做离线回测底座改造，TradingAgents 只适合做离线陪审团。

## 10. 护栏

- 不碰实盘；将来任何涉及下单的代码必须硬编码 `SIMULATE`。
- 不建定时任务；不动现行实盘纪律。
