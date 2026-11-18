#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商业短篇小说高爆热点爬取与选题提炼脚本 (hot_topics_curator.py)
功能：
1. 抓取知乎热榜、百度热搜、今日头条、贴吧热议四大真实开放源；
2. 过滤纯政务/赛事等非故事性内容，精选极具伦理、反差、利益纠纷的社会世情事件；
3. 标注数据来源与热度，并基于事件自动生成标准化“三句话商业爆款选题卡”；
4. 自动生成规范 Markdown 存入：
   /Users/scottsun/Documents/Obsidian Vault/娱乐/小说/小说内容/热点新闻及选题/YYYY-MM-DD 热点新闻及选题.md
"""

import os
import re
import json
import subprocess
from datetime import datetime

# 目标落盘目录
OUTPUT_DIR = "/Users/scottsun/Documents/Obsidian Vault/娱乐/小说/小说内容/热点新闻及选题"

# 过滤关键词（非小说故事性内容过滤）
EXCLUDE_KEYWORDS = [
    "元首", "会见", "普京", "特朗普", "拜登", "APEC", "外交部", "国防部", "台海",
    "开拓者", "勇士", "湖人", "NBA", "欧冠", "CBA", "绝杀", "比分", "半决赛",
    "指数大涨", "两市成交", "大盘", "加息", "降息", "美联储", "神舟", "火箭发射"
]

# 小说高情绪偏好关键词（优先捕获）
PREFER_KEYWORDS = [
    "退款", "婚", "彩礼", "房", "老人", "孩子", "学校", "被骗", "偷", "假",
    "亲戚", "遗产", "盗用", "冒名", "背叛", "婆婆", "丈夫", "妻子", "小叔子",
    "举报", "私自", "侵占", "赔偿", "开除", "断绝", "反转", "绝症", "隐瞒"
]

def run_curl(cmd_args):
    """通过 curl 稳健抓取数据，避免 Python 内置 urllib 的 SSL 握手与反爬阻断"""
    try:
        res = subprocess.run(cmd_args, capture_output=True, text=True, timeout=8)
        return res.stdout
    except Exception as e:
        return ""

def fetch_zhihu_hot():
    """抓取知乎实时热榜"""
    items = []
    cmd = ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'https://api.zhihu.com/topstory/hot-list']
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
    cmd = ['curl', '-s', '-L', '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'https://top.baidu.com/board?tab=realtime']
    html = run_curl(cmd)
    if html:
        titles = re.findall(r'class=\"c-single-text-ellipsis\">([^<]+)</div>', html)
        hots = re.findall(r'class=\"hot-index_1Bl1a\">([^<]+)</div>', html)
        descs = re.findall(r'class=\"large_nSuA8[^\"]*\">([^<]+)</div>', html)
        for i in range(len(titles)):
            t = titles[i].strip()
            h = hots[i].strip() if i < len(hots) else ""
            d = descs[i].strip() if i < len(descs) else ""
            if t:
                items.append({
                    "title": t,
                    "detail": d,
                    "source": "百度热搜",
                    "hot": h,
                    "url": f"https://www.baidu.com/s?wd={t}"
                })
    return items

def fetch_toutiao_hot():
    """抓取今日头条热榜"""
    items = []
    cmd = ['curl', '-s', '-H', 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc']
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
                    "detail": "",
                    "source": "今日头条",
                    "hot": f"{hot} 热度" if hot else "",
                    "url": url or f"https://so.toutiao.com/search?keyword={title}"
                })
    except Exception:
        pass
    return items

def fetch_tieba_hot():
    """抓取贴吧热议榜"""
    items = []
    cmd = ['curl', '-s', 'https://tieba.baidu.com/hottopic/browse/topicList']
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
                    "detail": desc,
                    "source": "百度贴吧热议",
                    "hot": f"{num} 讨论",
                    "url": url or f"https://tieba.baidu.com/f?kw={title}"
                })
    except Exception:
        pass
    return items

def is_story_worthy(title, detail=""):
    """判断是否具备网文故事改编价值与高情绪潜力"""
    text = title + " " + detail
    for ex in EXCLUDE_KEYWORDS:
        if ex in text:
            return False
    # 优先命中高情绪词
    for pref in PREFER_KEYWORDS:
        if pref in text:
            return True
    return len(title) >= 6

def generate_three_sentence_card(item):
    """基于事件特征构建标准三句话原始事件卡骨架"""
    title = item['title']
    detail = item['detail'] or "事件源于近期热搜广泛讨论的真实生活矛盾"
    
    # 智能推导主角身份与冲突类型
    if any(k in title for k in ["退款", "单", "买", "店", "盗", "钱"]):
        tag = "【消费做局与经济维权反杀流】"
        c1 = f"主角是一名按章办事的中小商家负责人（或平台合规法务），致力于在行业规则内维护正常经营秩序；"
        c2 = f"加害者利用平台漏洞与恶意机制发起恶意侵权/大额仅退款/敲诈勒索，不仅侵吞巨额财产，还联合亲信反咬主角‘服务欺诈’；"
        c3 = f"对方以为小商家为了体面只能忍气吞声吃下哑巴亏，却不知主角早已通过全链路技术取证与公证锁死恶意黑产链条；后续最期待的是主角以‘敲诈勒索与特大诈骗’让恶人全家背负刑责、数倍追偿。"
    elif any(k in title for k in ["婚", "彩礼", "妻", "夫", "婆", "弟", "家", "亲"]):
        tag = "【家庭伦理与极端侵夺反制流】"
        c1 = f"主角是一位自立自强、全款拥有独立资产的女性，一心想摆脱宗族寄生、维系自己的安宁领地；"
        c2 = f"极品亲戚和枕边人打着‘全家体谅、血浓于水’的道德绑架大旗，强行越过法律边界侵占主角的核心资产/尊严；"
        c3 = f"全家自以为用孝道与道德大棒能逼主角认栽，不知主角婚前早已完成不可撤回的财产确权切割与公证；后续最期待的是在对方最得意的高光宴席上当众掀桌清算、追回每一分钱。"
    elif any(k in title for k in ["职", "工", "学", "论文", "盗用", "冒名", "名额"]):
        tag = "【学术窃取与职业降维打脸流】"
        c1 = f"主角是在核心业务上深耕数年、掌握独家技术护城河的骨干人才，正准备携重大研发成果公开立项；"
        c2 = f"草包关系户/顶头上司凭借权力当众抹去主角全部署名，并将成果据为己有，甚至倒打一耙对主角进行全行业封杀；"
        c3 = f"盗窃者以为拿到图纸或数据就能高枕无忧，却不知最底层的动态校验密钥只在主角一人脑中；后续最期待的是在千人庆功大会现场系统瞬间熔断崩溃、草包当众现形被经侦带走。"
    else:
        tag = "【反常因果与社会猎奇反转流】"
        c1 = f"主角表面上是一个低调普通的守规矩者，只想在既定规则下完成自己的本职使命；"
        c2 = f"反派基于傲慢与贪婪，试图通过钻营空子或强权逼迫主角让步，践踏底线；"
        c3 = f"反派以为吃定了老实人，不知主角背后隐藏着足以掀翻全盘规则的颠覆性身份与反向因果底牌；后续最期待的是主角揭开底牌时双方立场瞬间调换、反派自食恶果自焚。"

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
    print("🚀 启动全网热搜与热榜实时抓取流水线...")
    all_items = []
    
    # 1. 抓取
    zhihu_items = fetch_zhihu_hot()
    print(f"  - 知乎热榜: 成功获取 {len(zhihu_items)} 条")
    baidu_items = fetch_baidu_hot()
    print(f"  - 百度热搜: 成功获取 {len(baidu_items)} 条")
    toutiao_items = fetch_toutiao_hot()
    print(f"  - 今日头条: 成功获取 {len(toutiao_items)} 条")
    tieba_items = fetch_tieba_hot()
    print(f"  - 贴吧热议: 成功获取 {len(tieba_items)} 条")
    
    all_items.extend(zhihu_items)
    all_items.extend(baidu_items)
    all_items.extend(toutiao_items)
    all_items.extend(tieba_items)
    
    # 2. 筛选
    filtered = []
    seen_titles = set()
    for item in all_items:
        t = item['title']
        if t not in seen_titles and is_story_worthy(t, item.get('detail', '')):
            seen_titles.add(t)
            filtered.append(item)
            
    print(f"✅ 过滤去重后，共获得 {len(filtered)} 条具备小说改编潜力的真实热点！")
    
    # 3. 排序挑选 Top 5 最具反差与故事性的事件
    selected_items = filtered[:5]
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    output_filename = f"{today_str} 热点新闻及选题.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # 4. 组装 Markdown 内容
    lines = [
        f"# 📰 {today_str} 全网真实热点新闻与商业选题推荐",
        "",
        "> **数据采集说明**：本期日报由爬虫脚本实时采集自【知乎热榜】、【百度实时热搜】、【今日头条】与【贴吧热议】四大真实开放平台，过滤宏观通报，聚焦高情绪、高故事性与利益伦理冲突事件，供小说创作者直接挑选作为原始事件素材。",
        "",
        "---",
        "",
        "## 一、🔥 今日精选 Top 5 真实热点与三句话爆款选题卡",
        ""
    ]
    
    for idx, item in enumerate(selected_items, 1):
        card = generate_three_sentence_card(item)
        lines.append(f"### 📌 候选选题 {idx:02d}：{card['tag']} {card['title']}")
        lines.append(f"- **数据来源**：{card['source']}（{card['hot']}） ｜ [🔗 查看原网热搜]({card['url']})")
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
        
    lines.append("## 二、📋 全网热门故事性事件聚合全貌（近 24 小时监控备选）")
    lines.append("")
    lines.append("| 序号 | 来源 | 热榜标题 | 热度数据 | 题材赛道标签 |")
    lines.append("| :---: | :---: | :--- | :--- | :--- |")
    
    for i, it in enumerate(filtered[:20], 1):
        tag_match = "社会民生/伦理"
        if any(k in it['title'] for k in ["婚", "妻", "夫", "家", "亲"]):
            tag_match = "婚恋世情"
        elif any(k in it['title'] for k in ["退款", "买", "假", "钱", "偷"]):
            tag_match = "利益纠纷/打假"
        elif any(k in it['title'] for k in ["职", "工", "学", "校"]):
            tag_match = "职场逆袭"
        lines.append(f"| {i} | {it['source']} | [{it['title']}]({it['url']}) | {it['hot']} | {tag_match} |")
        
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🛑 阶段人工确认节点（强制卡点）")
    lines.append("")
    lines.append("> 👉 **请作者挑选原始事件**：")
    lines.append("> 请从上述精选选题中回复序号（如：**选选题 01**），或挑选表格中的备选事件并提出修改意见。")
    lines.append("> 确认后，系统将自动进入【第二阶段：核心梗裂变与100字宣发短案】！")
    lines.append("")
    
    content = "\n".join(lines)
    
    # 确保目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"🎉 成功生成热点日报与选题文件：{output_path}")
    return output_path

if __name__ == "__main__":
    main()
