#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业短篇小说高爆热点爬取与选题提炼脚本 (hot_topics_curator.py) - 纯正大模型驱动版
功能：
1. 全平台真实抓取：今日头条、知乎热榜、百度热搜、贴吧热议四大真实开放源；
2. 过滤纯政务/赛事/宏观通报，深度捕获极具反差、利益纠纷、家庭伦理与社会猎奇的故事性事件；
3. 多源平衡精选算法：每个平台独立评分，挑出最炸裂、最具小说反转张力的话题进入 Top 5；
4. 真正调用底层大模型（LLM Batch Generation），彻底杜绝任何硬编码模版；
5. 分平台建立完整全景监控表格（今日头条、知乎、百度热搜、贴吧热议各成独立专区）；
6. 自动生成包含 Hook、角色身份、阻碍事件、反差底牌的深度故事卡，并落盘至：
   /Users/scottsun/Documents/Obsidian Vault/娱乐/小说/小说内容/热点新闻及选题/YYYY-MM-DD 热点新闻及选题.md
"""

import os
import re
import json
import subprocess
from datetime import datetime

# 目标落盘目录
OUTPUT_DIR = "/Users/scottsun/Documents/Obsidian Vault/娱乐/小说/小说内容/热点新闻及选题"

# 严格过滤宏观、外交、赛事等非故事性关键词
EXCLUDE_KEYWORDS = [
    "元首", "会见", "普京", "特朗普", "拜登", "李在明", "APEC", "外交部", "国防部", "台海",
    "开拓者", "勇士", "湖人", "NBA", "欧冠", "CBA", "绝杀", "比分", "半决赛", "国足",
    "指数大涨", "两市成交", "大盘", "加息", "降息", "美联储", "神舟", "火箭发射", 
    "停满", "专机", "芯片", "中方回应", "台湾", "统一", "两国", "合作", "总理", "总统",
    "大桥", "导弹", "东道主", "排面", "接机", "国台办", "新图景", "盛赞", "自贸区",
    "出访", "握手", "安保", "大会", "峰会"
]

# 小说高情绪/冲突加分词库
HIGH_STORY_SIGNALS = {
    # 婚恋家庭重磅炸弹
    "非亲生": 200, "亲子鉴定": 200, "出轨": 150, "彩礼": 150, "抚养权": 150, "财产转移": 160,
    "亲弟弟": 140, "重男轻女": 140, "扶弟魔": 140, "吸血": 140, "婆婆": 130, "小叔子": 130,
    "遗产": 140, "断绝关系": 150, "倒贴": 130, "养老": 120, "拆迁款": 140, "鸠占鹊巢": 160,
    # 利益侵夺与规则做局
    "仅退款": 160, "退款": 120, "诈骗": 130, "拘留": 120, "套路": 110, "打假": 120,
    "烤全羊": 130, "缺斤少两": 130, "阴阳合同": 140, "侵占": 130, "敲诈": 130,
    "索赔": 110, "掀桌": 140, "判刑": 120, "反杀": 140,
    # 职场学术掠夺与降维打击
    "论文": 130, "学术造假": 150, "顶替": 150, "冒名": 150, "开除": 110, "通报": 110,
    "读博": 100, "抢功劳": 140, "工亡": 120, "潜规则": 130,
    # 奇观猎奇与网络深层热梗
    "麦穗与羊": 150, "破防": 110, "反转": 120, "笑不出来": 130, "涨粉": 100
}

def run_curl(cmd_args):
    """通过 curl 稳健抓取数据"""
    try:
        res = subprocess.run(cmd_args, capture_output=True, text=True, timeout=10)
        return res.stdout
    except Exception:
        return ""

def calculate_story_score(title, detail=""):
    """计算话题的网文改编爆发力得分"""
    text = title + " " + detail
    for ex in EXCLUDE_KEYWORDS:
        if ex in text:
            return -999  # 彻底排除
    score = 10  # 基础分
    for kw, val in HIGH_STORY_SIGNALS.items():
        if kw in text:
            score += val
    if len(title) >= 8:
        score += 10
    return score

def fetch_toutiao_hot():
    """抓取今日头条热榜"""
    items = []
    cmd = [
        'curl', '-s',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        '-H', 'Referer: https://www.toutiao.com/',
        'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc'
    ]
    raw = run_curl(cmd)
    try:
        data = json.loads(raw)
        for entry in data.get('data', []):
            title = entry.get('Title', '').strip()
            hot = str(entry.get('HotValue', ''))
            url = entry.get('Url', '')
            if title:
                items.append({
                    "title": title,
                    "detail": "今日头条实时热搜高讨论社会世情切片",
                    "source": "今日头条",
                    "hot": f"{hot} 热度" if hot else "热门",
                    "url": url or f"https://so.toutiao.com/search?keyword={title}"
                })
    except Exception:
        pass
    return items

def fetch_zhihu_hot():
    """抓取知乎实时热榜"""
    items = []
    cmd = [
        'curl', '-s',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'https://api.zhihu.com/topstory/hot-list'
    ]
    raw = run_curl(cmd)
    try:
        data = json.loads(raw)
        for entry in data.get('data', []):
            target = entry.get('target', {})
            title = target.get('title', '').strip()
            detail = target.get('excerpt', '').strip()
            hot_text = entry.get('detail_text', '')
            url = f"https://www.zhihu.com/question/{target.get('id')}"
            if title:
                items.append({
                    "title": title,
                    "detail": detail,
                    "source": "知乎热榜",
                    "hot": hot_text,
                    "url": url
                })
    except Exception:
        pass
    return items

def fetch_baidu_hot():
    """抓取百度实时热搜"""
    items = []
    cmd = [
        'curl', '-s', '-L',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'https://top.baidu.com/board?tab=realtime'
    ]
    html = run_curl(cmd)
    if html:
        titles = re.findall(r'class=\"c-single-text-ellipsis\">([^<]+)</div>', html)
        hots = re.findall(r'class=\"hot-index_1Bl1a\">([^<]+)</div>', html)
        for i in range(len(titles)):
            t = titles[i].strip()
            h = hots[i].strip() if i < len(hots) else ""
            if t:
                items.append({
                    "title": t,
                    "detail": "百度指数实时飙升大众关切热点",
                    "source": "百度热搜",
                    "hot": f"{h} 搜索指数" if h else "热搜",
                    "url": f"https://www.baidu.com/s?wd={t}"
                })
    return items

def fetch_tieba_hot():
    """抓取贴吧热议榜"""
    items = []
    cmd = [
        'curl', '-s',
        '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'https://tieba.baidu.com/hottopic/browse/topicList'
    ]
    raw = run_curl(cmd)
    try:
        data = json.loads(raw)
        for entry in data.get('data', {}).get('bang_topic', {}).get('topic_list', []):
            title = entry.get('topic_name', '').strip()
            desc = entry.get('topic_desc', '').strip()
            num = entry.get('discuss_num', 0)
            url = entry.get('topic_url', '')
            if title:
                items.append({
                    "title": title,
                    "detail": desc or "百度贴吧年轻网民高度争议与共鸣切片",
                    "source": "百度贴吧",
                    "hot": f"{num} 讨论",
                    "url": url or f"https://tieba.baidu.com/f?kw={title}"
                })
    except Exception:
        pass
    return items

def batch_generate_cards_with_llm(selected_items):
    """
    通过底层大模型 CLI 进行批量深度 IP 剧情提炼
    严格杜绝任何硬编码映射，深度绑定真实新闻事实
    """
    print("🤖 正在调用大模型进行剧情深度推演与高概念反差提炼（Batch Mode）...")
    
    prompt_items = []
    for it in selected_items:
        # 裁剪过长的新闻摘要，确保提示词精准紧凑，防止超时
        det = (it.get('detail', '') or it['title'])[:140]
        prompt_items.append({
            "title": it['title'],
            "source": it['source'],
            "hot": it['hot'],
            "detail": det
        })

    prompt = f"""你是一名顶级网络短篇小说金牌主编与爆款IP策划专家。
请根据以下精选的真实热点新闻，为每一条量身定制提炼一个极具反差感、爆款脑洞的商业短篇故事选题卡。

【真实新闻列表】
{json.dumps(prompt_items, ensure_ascii=False, indent=2)}

【设计核心要求】
1. 绝对严禁使用任何模版化套话！必须深度吃透每一条新闻的具体事实细节（如金额、年份、荒诞行径、具体当事人身份等）进行具象的戏剧化推演；
2. 融入爆款高概念反差（如《文曲星》式的剥夺式打脸、降维打击、因果反噬等），拒绝平庸老套的低级撕逼；
3. 输出纯 JSON 数组，每个对象严格包含：
[
  {{
    "title": "原新闻标题",
    "tag": "精准故事赛道标签（如：【婚恋绝户·基因因果反噬与剥夺流】）",
    "hook": "一句话惊艳反差核心梗（直击痛点与反转）",
    "c1": "【主角是谁，准备做什么】（必须绑定具象职业、当事人处境与当下目标）",
    "c2": "【谁因为什么阻碍或者伤害了主角】（深度融合新闻真实的背叛、掠夺或荒诞行为）",
    "c3": "【双方不知道的反差是什么，后面最值得期待的是什么】（双方底牌信息差、核心反杀看点与高潮爽点）"
  }}
]
只需返回标准 JSON 数组，严格以 [ 开头，以 ] 结尾，不要包含 Markdown 标记或其他多余文字。"""

    cmd = ['/Users/scottsun/.gemini/bin/agy', '-p', prompt, '--model', 'gemini-3.8-flash-low', '--disable-slash-commands']
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
        out = res.stdout.strip()
        m = re.search(r'\[.*\]', out, re.DOTALL)
        if m:
            cards = json.loads(m.group(0))
            print(f"✅ 大模型成功返回 {len(cards)} 个深度提炼的故事卡！")
            return cards
        else:
            print("⚠️ 未正则匹配到 JSON 数组，输出为:", out[:300])
    except Exception as e:
        print(f"⚠️ 大模型调用解析异常: {e}")
        
    return []

def main():
    print("🚀 启动全网四大平台实时抓取流水线...")
    
    # 1. 抓取各源
    toutiao_items = fetch_toutiao_hot()
    print(f"  - 今日头条: 成功获取 {len(toutiao_items)} 条")
    
    zhihu_items = fetch_zhihu_hot()
    print(f"  - 知乎热榜: 成功获取 {len(zhihu_items)} 条")
    
    baidu_items = fetch_baidu_hot()
    print(f"  - 百度热搜: 成功获取 {len(baidu_items)} 条")
    
    tieba_items = fetch_tieba_hot()
    print(f"  - 贴吧热议: 成功获取 {len(tieba_items)} 条")
    
    # 2. 分别打分与排序
    def score_items(items):
        res = []
        for it in items:
            s = calculate_story_score(it['title'], it.get('detail', ''))
            if s > 0:
                it['score'] = s
                res.append(it)
        res.sort(key=lambda x: x['score'], reverse=True)
        return res

    tt_scored = score_items(toutiao_items)
    zh_scored = score_items(zhihu_items)
    bd_scored = score_items(baidu_items)
    tb_scored = score_items(tieba_items)
    
    print(f"✅ 严格打分后故事性热点分布：今日头条 {len(tt_scored)} 条 | 知乎 {len(zh_scored)} 条 | 百度 {len(bd_scored)} 条 | 贴吧 {len(tb_scored)} 条")
    
    # 3. 均衡挑选 Top 5：各大平台第一名直接出战，确保 100% 涵盖各源
    selected_items = []
    if tt_scored:
        selected_items.append(tt_scored[0])
    if zh_scored:
        selected_items.append(zh_scored[0])
    if bd_scored:
        selected_items.append(bd_scored[0])
    if tb_scored:
        selected_items.append(tb_scored[0])
    # 补充第 5 个（从头条或知乎的次高分中选）
    candidates_5th = []
    if len(tt_scored) > 1: candidates_5th.append(tt_scored[1])
    if len(zh_scored) > 1: candidates_5th.append(zh_scored[1])
    if len(bd_scored) > 1: candidates_5th.append(bd_scored[1])
    if candidates_5th:
        candidates_5th.sort(key=lambda x: x['score'], reverse=True)
        selected_items.append(candidates_5th[0])

    # 4. 调用真实大模型批量生成高概念爆款选题卡
    llm_cards = batch_generate_cards_with_llm(selected_items)
    card_map = {c['title']: c for c in llm_cards if 'title' in c}

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"{today_str} 热点新闻及选题.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # 5. 组装 Markdown 内容
    lines = [
        f"# 📰 {today_str} 全网真实热点新闻与商业选题推荐（大模型深度提炼版）",
        "",
        "> **数据采集与提炼说明**：本期日报由爬虫脚本实时采集自【今日头条】、【知乎热榜】、【百度实时热搜】与【百度贴吧】四大开放源，经故事性打分算法过滤后，**由底层大模型深度结合新闻细节进行一对一 IP 剧情推演与三句话商业选题卡提炼**，杜绝任何模板化套话，供创作者直接挑选作为原始事件素材。",
        "",
        "---",
        "",
        "## 一、🔥 今日四大平台代表作 Top 5 爆款选题卡（大模型深度定制）",
        ""
    ]
    
    for idx, item in enumerate(selected_items, 1):
        t = item['title']
        card = card_map.get(t)
        
        tag = card.get('tag', '【商业短篇热点流】') if card else '【商业短篇热点流】'
        hook = card.get('hook', '') if card else ''
        c1 = card.get('c1', '') if card else ''
        c2 = card.get('c2', '') if card else ''
        c3 = card.get('c3', '') if card else ''
        
        lines.append(f"### 📌 候选选题 {idx:02d}：{tag} {t}")
        lines.append(f"- **数据来源**：**{item['source']}**（{item['hot']}） ｜ [🔗 查看原网热搜]({item['url']})")
        if item.get('detail'):
            lines.append(f"- **真实事件摘要**：{item['detail']}")
        if hook:
            lines.append(f"- **⚡ 惊艳核心梗（Hook）**：{hook}")
        lines.append("- **三句话标准原始事件卡（大模型定制推演）**：")
        lines.append(f"  1. **{c1}**" if c1.startswith("【") else f"  1. **【主角是谁，准备做什么】**：{c1}")
        lines.append(f"  2. **{c2}**" if c2.startswith("【") else f"  2. **【谁因为什么阻碍或者伤害了主角】**：{c2}")
        lines.append(f"  3. **{c3}**" if c3.startswith("【") else f"  3. **【双方不知道的反差是什么，后面最值得期待的是什么】**：{c3}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 6. 分平台全量聚合监控区（头条、知乎、百度、贴吧独立成表）
    lines.append("## 二、📋 四大平台热搜全景备选库（分类分表查看）")
    lines.append("")
    
    def render_table(source_name, items):
        t_lines = [f"### 🌐 【{source_name}】故事性热点备选（共 {len(items)} 条）", ""]
        t_lines.append("| 序号 | 热搜标题 | 实时数据 | 故事性得分 |")
        t_lines.append("| :---: | :--- | :--- | :---: |")
        for i, it in enumerate(items, 1):
            t_lines.append(f"| {i} | [{it['title']}]({it['url']}) | {it['hot']} | {it['score']} 分 |")
        t_lines.append("")
        return t_lines

    lines.extend(render_table("今日头条", tt_scored))
    lines.extend(render_table("知乎热榜", zh_scored))
    lines.extend(render_table("百度实时热搜", bd_scored))
    lines.extend(render_table("百度贴吧热议", tb_scored))
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"🎉 成功生成大模型驱动的热点日报与选题文件：{output_path}")

if __name__ == "__main__":
    main()
