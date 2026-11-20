# 📚 Novel Master: Professional Fiction Writing AI Agent System
# 小说全流程双轨工业化创作智能体体系 (Novel Master 4.0)

> **Zero-Setup · Pure Markdown Architecture · Multi-Agent SOP**  
> Compatible with **Claude Code**, **Cursor**, **Windsurf**, **Copilot**, and 20+ AI Coding / Agent Environments.

---

## 🌟 Overview / 系统概述

**Novel Master** is an enterprise-grade fiction creation system specifically engineered for commercial web fiction and viral short stories. 
Unlike typical free-form LLM writing prompts that hallucinate, lose long-term memory, or produce cliché AI-sounding prose, Novel Master implements a **rigorous industrial SOP (Standard Operating Procedure)** with forced human confirmation checkpoints at each milestone.

**Novel Master** 是专为商业网络小说与高爆短篇故事打造的专业级工业化创作系统。
彻底告别传统 AI 写作中常见的“剧情注水、战力崩塌、中途遗忘设定、八股AI机械味”等顽疾，采用**分阶段强制人机协同确认卡点机制**，实现高完成度、高追读率的精品商业创作。

---

## 🚀 Dual-Track Architecture / 长短篇双轨总控

| Track / 专区 | Agent Command / 触发指令 | Target Length / 目标篇幅 | Core Pipeline / 核心流水线 | Target Platforms / 适用平台 |
| :--- | :--- | :--- | :--- | :--- |
| **📕 Short Fiction<br>短篇小说总控** | `novel-short-master`<br>*(写短篇 / 短篇总控)* | **8,000 ~ 15,000 words**<br>(Single Chapter Single Story) | 1. Topic & 3-Sentence Card<br>2. Hook & 100-Word Promo Copy<br>3. 200~400 Word Golden Lead Hook<br>4. 4000-Word Paywall Outline & 5 Checks<br>5. High-Density Anti-AI Prose | Zhihu Yansuan (知乎盐选), Fanqie Stories (番茄短故事), WeChat/Xiaohongshu Articles |
| **📘 Long Web Novel<br>长篇小说总控** | `novel-long-master`<br>*(写长篇 / 长篇总控)* | **300,000 ~ 2,000,000+ words**<br>(Multi-Volume Serialization) | 1. Long-term Selling Points & Cheat System<br>2. Worldbuilding & 9~12 Power Tiers<br>3. Golden 3-Chapter Opening Breakdown<br>4. Multi-Volume Blueprint & Chapter Outlines<br>5. Serialized Writing (2k-3k words/ch) + Foreshadowing Ledger & State Machine | Qidian (起点中文网), Fanqie Serialization (番茄小说), Jinjiang (晋江), Zongheng (纵横) |

---

## 🛠️ Key Innovations / 核心技术突破

### 1. Zero-Setup & Zero-Dependency (零配置即用)
- 100% pure Markdown and structured prompt protocols (`SKILL.md`).
- **No external Python dependencies, no local network scraper setup required.** Works instantly inside any standard Agent sandbox.

### 2. Forced Human-in-the-Loop Checkpoints (强制人机卡点)
- AI never runs ahead blindly. At every critical stage (topic, hook, lead, outline), the system pauses and waits for author approval before moving forward.

### 3. Anti-AI Detection Rules (严格抗 AI 检测军规)
- Enforces strict stylistic bans against typical LLM hallmarks:
  - ❌ No triple-negative parallel sentences (*"没有愤怒，没有慌乱，甚至连..."*);
  - ❌ No exposition dumps through dialogue;
  - ❌ No disposable NPCs reading legal/contract rulebooks to the reader;
  - ❌ No checklist-style physiological declarations (*"冷汗浸透后背"*).

### 4. Long-Novel State Machine & Foreshadowing Ledger (长篇状态机与防崩账本)
- Automatically tracks protagonist cultivation tier, inventory, and faction relationships per chapter.
- Maintains a dedicated Foreshadowing Ledger (伏笔台账) to prevent forgotten plot holes over millions of words.

---

## 📂 Repository Structure / 仓库目录结构

```text
├── 短篇专区 (novel-short)
│   ├── SKILL.md                 # Short Fiction Master Agent (novel-short-master)
│   ├── 短篇_总控中枢.md          # 5-Stage Short Fiction SOP & Workflow
│   ├── 短篇_选题挖掘.md          # Topic Curation & 3-Sentence Event Card
│   ├── 短篇_核心梗裂变.md        # 4D Event Deconstruction & 100-Word Promo Copy
│   ├── 短篇_导语创作.md          # 200~400 Word Golden Lead Hook
│   ├── 短篇_单篇大纲.md          # 4000-Word Cliffhanger Outline & 5 Causality Checks
│   ├── 短篇_正文执笔.md          # 8k~12k Word High-Density Prose
│   └── 短篇_毒舌审校.md          # Commercial Review & Anti-AI Audit
│
├── 长篇专区 (novel-long)
│   ├── SKILL.md                 # Long Novel Master Agent (novel-long-master)
│   ├── 长篇_总控中枢.md          # Long Serialization SOP & Milestone Control
│   ├── 长篇_卖点与金手指.md      # Golden Finger Mechanism & Long-term Motivation
│   ├── 长篇_世界观与战力.md      # 9~12 Cultivation Tier Matrix & Faction Maps
│   ├── 长篇_黄金前三章.md        # Golden 3-Chapter Breaking Opening Guide
│   ├── 长篇_分卷与章纲.md        # Multi-Volume Blueprint & Chapter Outlines
│   ├── 长篇_连载执笔.md          # 2k~3k Word Chapter Writing & 4 Cliffhanger Skills
│   ├── 长篇_伏笔台账.md          # Foreshadowing Lifecycle Tracking Ledger
│   ├── 长篇_长程记忆与状态机.md  # Dynamic State Snapshot & Memory Engine
│   └── 长篇_连载审校.md          # Reader Retention & Pacing Quality Audit
│
├── 通用资源 (shared)
│   ├── 抗AI检测军规.md           # Anti-AIGC Stylistic Writing Guide
│   ├── 考据推演引擎.md           # Fact-checking & Logical Deduction Engine
│   └── 题材风格库/               # Curated Sub-Genre Style Guides
│
├── SKILL.md                     # Universal Router Entry (novel-master)
└── README.md                    # System Documentation
```

---

## ⚡ Quick Start / 快速开始

### Installation in Agent Tools / 安装方式

1. **Claude Code / Cursor / Windsurf / Antigravity**:
   Clone or copy this repository into your agent's skills directory:
   ```bash
   git clone https://github.com/Sun-tech2020/novel-master.git ~/.gemini/config/skills/novel-master
   ```

2. **Triggering in Chat / 对话呼叫**:
   - To write a short viral story: type **`短篇小说总控`** or **`write short story`**
   - To plan a serialized novel: type **`长篇小说总控`** or **`write long novel`**

---

## 📄 License & Attribution

- Author: [Zhuoqun Sun (Scott Sun)](https://github.com/Sun-tech2020)
- License: MIT License - free for commercial and personal usage.
