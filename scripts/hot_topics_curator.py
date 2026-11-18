#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业短篇小说高爆热点爬取与选题提炼脚本 (hot_topics_curator.py)
功能：
1. 全平台真实抓取：今日头条、知乎热榜、百度热搜、贴吧热议四大真实开放源；
2. 过滤纯政务/赛事/宏观通报，深度捕获极具反差、利益纠纷、家庭伦理与社会猎奇的故事性事件；
3. 多源平衡精选算法：每个平台独立评分，挑出最炸裂、最具小说反转张力的话题进入 Top 5；
4. 分平台建立完整全景监控表格（今日头条、知乎、百度热搜、贴吧热议各成独立专区）；
5. 自动生成标准化“三句话商业爆款选题卡”，并落盘至：
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
    "新图景", "出访", "握手", "安保", "大会", "峰会"
]

# 小说高情绪/冲突加分词库
HIGH_STORY_SIGNALS = {
    # 婚恋家庭重磅炸弹（得分 +150）
    "非亲生": 200, "亲子鉴定": 200, "出轨": 150, "彩礼": 150, "抚养权": 150, "财产转移": 160,
    "亲弟弟": 140, "重男轻女": 140, "扶弟魔": 140, "吸血": 140, "婆婆": 130, "小叔子": 130,
    "遗产": 140, "断绝关系": 150, "倒贴": 130, "养老": 120, "拆迁款": 140, "鸠占鹊巢": 160,
    # 利益侵夺与规则做局（得分 +120）
    "仅退款": 160, "退款": 120, "诈骗": 130, "拘留": 120, "套路": 110, "打假": 120,
    "烤全羊": 130, "缺斤少两": 130, "阴阳合同": 140, "侵占": 130, "敲诈": 130,
    "索赔": 110, "掀桌": 140, "判刑": 120, "反杀": 140,
    # 职场学术掠夺与降维打击（得分 +110）
    "论文": 130, "学术造假": 150, "顶替": 150, "冒名": 150, "开除": 110, "通报": 110,
    "读博": 100, "抢功劳": 140, "工亡": 120, "潜规则": 130,
    # 奇观猎奇与网络深层热梗（得分 +100）
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

def generate_three_sentence_card(item):
    """基于事件特征构建标准三句话原始事件卡骨架"""
    title = item['title']
    detail = item['detail'] or "事件源于近期热搜广泛讨论的真实生活矛盾"
    
    # 针对不同核心冲突设计量身定做的人设与反杀机制
    if any(k in title for k in ["非亲生", "婚", "彩礼", "妻", "夫", "子女"]):
        tag = "【婚恋欺瞒与亲情资产掀桌反杀流】"
        c1 = "主角表面上是多年来倾尽所有、勤勤恳恳维系家庭和抚育子女的老实丈夫（或妻子）；"
        c2 = "枕边人联合原生家庭长期暗度陈仓、不仅隐瞒孩子血统真相转移巨额财产，还在高光时刻倒打一耙逼迫主角净身出户；"
        c3 = "全家以为老实人被蒙在鼓里只能认命吞声，不知主角早已通过全套基因断代鉴定公证与洗钱证据链锁定胜局；后续最期待的是在反派满月宴/庆功宴现场公证书与法院传票当头砸下，恶人全家涉嫌诈骗净身出户、彻底沦为全网笑柄。"
    elif any(k in title for k in ["退款", "单", "买", "店", "盗", "钱", "赔", "羊", "肉", "价"]):
        tag = "【消费做局与经济维权硬核反杀流】"
        c1 = "主角是一名恪尽职守、掌握核心合规凭证与行业底层的从业者（或硬核消费者）；"
        c2 = "利益作恶方利用平台规则漏洞疯狂薅羊毛侵夺资产、恶意仅退款几百次，或者商家店大欺客缺斤少两反咬消费者寻衅滋事；"
        c3 = "作恶者以为主角人微言轻只能吃哑巴亏，却不知主角早已通过隐形物证溯源、不可篡改电子证据完成全链路收网；后续最期待的是执法机关雷霆上门，以‘特大敲诈勒索与诈骗罪’将恶人全家刑事拘留并处数倍顶格追偿。"
    elif any(k in title for k in ["弟弟", "老人", "婆", "弟", "家", "亲", "拍老人"]):
        tag = "【宗族吸血与重男轻女反绑架流】"
        c1 = "主角是原生家庭中唯一凭借自己双手打拼出独立资产、准备迈入崭新生活的清醒独立者；"
        c2 = "宗族长辈打着‘血浓于水、长兄如父/长姐如母’的道德大棒，在高龄生子或挥霍亏空后强行要求主角出钱买房、给幼弟当一辈子血包；"
        c3 = "吸血亲属自恃道德绑架吃定了晚辈，不知主角早已完成不可撤销的财产所有权公证与断亲法律程序；后续最期待的是在对方大肆宴请亲友强逼过户的现场当众公开账单与断绝文书，彻底粉碎吸血幻想。"
    elif any(k in title for k in ["论文", "学", "博", "研究", "工", "AI"]):
        tag = "【学术职场与名誉剥夺降维流】"
        c1 = "主角是在核心业务上隐姓埋名、手握关键专利与核心突破的真正骨干研发者；"
        c2 = "学术阀门/草包关系户在重磅评审前夕强行顶替第一作者，用AI或拼凑造假抢走所有荣誉并将主角当场解雇封杀；"
        c3 = "窃取者以为拿到报告就能高枕无忧，不知核心动态校验代码与物理模型底牌仅在主角脑中；后续最期待的是在万众瞩目的国字号科技发布会上系统全面报错宕机、草包当众现形被学术委员会与经侦联手带走。"
    else:
        tag = "【社会猎奇与时代痛感反转流】"
        c1 = "主角表面上是一个按规矩办事的普通守序人，正按部就班推进一项看似不起眼的平凡追求；"
        c2 = "外界偏见或特权反派凭借信息差与傲慢做派，肆意践踏纯粹情感与规则底线，企图用权势抹杀主角的一切心血；"
        c3 = "霸凌者以为吃定了底层，不知主角手中保留着足以掀翻整场虚伪游戏的关键信物与逆风翻盘底牌；后续最期待的是在聚光灯下真相大白，施暴者苦心经营的体面彻底粉碎、原告当庭沦为被告。"

    return {
        "tag": tag,
        "title": title,
        "source": item['source'],
        "hot": item['hot'],
        "url": item['url'],
        "detail": detail,
        "c1": c1,
        "c2": c2,
        "c3": c3
    }

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

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"{today_str} 热点新闻及选题.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # 4. 组装 Markdown 内容
    lines = [
        f"# 📰 {today_str} 全网真实热点新闻与商业选题推荐（四大平台多源综合版）",
        "",
        "> **数据采集说明**：本期日报由爬虫脚本实时采集自【今日头条】、【知乎热榜】、【百度实时热搜】与【百度贴吧】四大开放源，严密过滤纯政务/赛事噪音，深度挖掘极具反差、利益侵夺与人伦纠葛的故事性切片，供创作者直接挑选作为原始事件素材。",
        "",
        "---",
        "",
        "## 一、🔥 今日四大平台代表作 Top 5 爆款选题卡",
        ""
    ]
    
    for idx, item in enumerate(selected_items, 1):
        card = generate_three_sentence_card(item)
        lines.append(f"### 📌 候选选题 {idx:02d}：{card['tag']} {card['title']}")
        lines.append(f"- **数据来源**：**{card['source']}**（{card['hot']}） ｜ [🔗 查看原网热搜]({card['url']})")
        if card['detail']:
            lines.append(f"- **真实事件摘要**：{card['detail']}")
        lines.append("- **推荐理由**：直击现实人际边界侵犯与利益剥夺痛点，具有强烈的反常性、憋屈感与极致反杀预期。")
        lines.append("- **三句话标准原始事件卡**：")
        lines.append(f"  1. **【主角是谁，准备做什么】**：{card['c1']}")
        lines.append(f"  2. **【谁因为什么阻碍或者伤害了她】**：{card['c2']}")
        lines.append(f"  3. **【双方不知道的反差是什么，后面最值得期待的是什么】**：{card['c3']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 5. 分平台全量聚合监控区（头条、知乎、百度、贴吧独立成表）
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
        
    print(f"🎉 成功生成多源热点日报与选题文件：{output_path}")

if __name__ == "__main__":
    main()
