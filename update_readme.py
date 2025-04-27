import os
import re
from datetime import datetime, timedelta
import difflib


def scan_notes(directory="notes"):
    """
    扫描指定目录下的所有 Markdown 文件，并按修改时间从新到旧排序。
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"指定的目录不存在: {directory}")

    notes = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                notes.append(os.path.join(root, file))
    notes.sort(key=os.path.getmtime, reverse=True)
    return notes


def categorize_notes_by_month(notes):
    """
    按年月分类笔记，返回字典，键为年月（如202504），值为对应笔记路径列表。
    """
    notes_by_month = {}
    for note in notes:
        mod_time = datetime.fromtimestamp(os.path.getmtime(note))
        year_month = mod_time.strftime("%Y%m")
        notes_by_month.setdefault(year_month, []).append(note)
    return notes_by_month


def get_recent_notes(notes, days=7):
    """
    获取最近 N 天内修改的笔记。
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    return [note for note in notes if datetime.fromtimestamp(os.path.getmtime(note)) >= cutoff_date]


def find_pinned_notes(notes):
    """
    查找置顶笔记，通过检查笔记内容中是否包含 #置顶 标签。
    """
    pinned_notes = []
    for note in notes:
        try:
            with open(note, "r", encoding="utf-8") as file:
                content = file.read()
                if "#置顶" in content or "#pinned" in content:
                    pinned_notes.append(note)
        except Exception:
            # 如果读取文件出错，跳过该文件
            continue
    return pinned_notes


def find_first_image_in_notes(notes):
    """
    从笔记中查找第一张图片，返回图片路径（如果有）。
    """
    for note in notes:
        with open(note, "r", encoding="utf-8") as file:
            content = file.read()
            match = re.search(r"!\[.*?\]\((.*?)\)", content)
            if match:
                return match.group(1)
    return None


def extract_keywords(content, num_keywords=10):
    """
    从笔记内容中提取关键词。
    """
    # 简单实现：移除常见停用词，按词频排序
    stop_words = {'的', '了', '和', '是', '在', '我', '有', '这', '个', '你', '们', '与', '或', '为', '以', '及', '但', '并', '等'}
    words = re.findall(r'[\w\u4e00-\u9fff]+', content.lower())
    keywords = [word for word in words if word not in stop_words and len(word) > 1]
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # 按词频排序并返回前N个关键词
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_keywords[:num_keywords]]


def find_related_notes(target_note, all_notes, max_related=5):
    """
    查找与目标笔记相关的其他笔记。
    使用内容相似度和关键词匹配来确定相关性。
    """
    if target_note not in all_notes:
        return []
    
    try:
        with open(target_note, "r", encoding="utf-8") as file:
            target_content = file.read()
    except Exception:
        return []
    
    target_keywords = extract_keywords(target_content)
    
    related_scores = []
    for note in all_notes:
        if note == target_note:  # 跳过自身
            continue
        
        try:
            with open(note, "r", encoding="utf-8") as file:
                note_content = file.read()
                
            # 计算内容相似度
            similarity = difflib.SequenceMatcher(None, target_content, note_content).ratio()
            
            # 计算关键词匹配度
            note_keywords = extract_keywords(note_content)
            keyword_matches = len(set(target_keywords) & set(note_keywords))
            
            # 综合评分 (可以调整权重)
            score = similarity * 0.6 + (keyword_matches / max(len(target_keywords), 1)) * 0.4
            
            related_scores.append((note, score))
        except Exception:
            continue
    
    # 按相关性排序并返回前N个
    related_scores.sort(key=lambda x: x[1], reverse=True)
    return [note for note, _ in related_scores[:max_related]]


def update_note_with_related_links(note, related_notes):
    """
    在笔记底部添加相关笔记的链接。
    如果已经存在相关笔记部分，则更新它。
    """
    if not related_notes:
        return False
    
    try:
        with open(note, "r", encoding="utf-8") as file:
            content = file.read()
        
        # 检查是否已有相关笔记部分
        related_section_pattern = r"\n## 相关笔记\n[\s\S]*?(\n##|\Z)"
        related_section_match = re.search(related_section_pattern, content)
        
        # 准备新的相关笔记部分
        related_links = "\n## 相关笔记\n\n"
        for related_note in related_notes:
            note_name = os.path.basename(related_note)
            related_links += f"- [{note_name}]({related_note})\n"
        related_links += "\n"
        
        # 更新或添加相关笔记部分
        if related_section_match:
            # 更新已有部分
            updated_content = content[:related_section_match.start()] + related_links
            if related_section_match.group(1) != "\Z":
                updated_content += content[related_section_match.start() + len(related_section_match.group(0)) - 1:]
        else:
            # 添加到文件末尾
            updated_content = content.rstrip() + "\n\n" + related_links
        
        # 写回文件
        with open(note, "w", encoding="utf-8") as file:
            file.write(updated_content)
        
        return True
    except Exception as e:
        print(f"更新笔记 {note} 失败: {e}")
        return False


def generate_readme_content(notes_by_month, recent_notes, recent_image, pinned_notes):
    """
    根据笔记分类、最近笔记、最近插图和置顶笔记生成 README 内容。
    """
    readme_content = "# 笔记目录\n\n"

    # 最近更新时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content += f"**最近更新时间：{now}**\n\n"

    # 最近的插图
    if recent_image:
        readme_content += f"![最近插图]({recent_image})\n\n"
    
    # 置顶笔记
    if pinned_notes:
        readme_content += "## 📌 置顶笔记\n\n"
        for note in pinned_notes:
            note_name = os.path.basename(note)
            readme_content += f"- [{note_name}]({note})\n"
        readme_content += "\n"

    # 最近 7 天的笔记
    readme_content += "## 最近 7 天的笔记\n\n"
    for note in recent_notes:
        note_name = os.path.basename(note)
        readme_content += f"- [{note_name}]({note})\n"
    readme_content += "\n"

    # 按年月分类的笔记
    readme_content += "## 按年月分类的笔记\n\n"
    for year_month, notes in notes_by_month.items():
        readme_content += f"### {year_month}\n\n"
        for note in notes:
            note_name = os.path.basename(note)
            readme_content += f"- [{note_name}]({note})\n"
        readme_content += "\n"

    return readme_content


def update_readme():
    """
    主函数，扫描笔记并生成 README 文件。
    """
    notes_dir = "notes"
    notes = scan_notes(notes_dir)
    notes_by_month = categorize_notes_by_month(notes)
    recent_notes = get_recent_notes(notes)
    pinned_notes = find_pinned_notes(notes)
    recent_image = find_first_image_in_notes(notes)

    # 为每个笔记添加相关笔记链接
    print("正在为笔记添加相关链接...")
    updated_count = 0
    for note in notes:
        related_notes = find_related_notes(note, notes)
        if related_notes and update_note_with_related_links(note, related_notes):
            updated_count += 1
    print(f"已更新 {updated_count} 个笔记的相关链接")

    # 生成 README 内容
    readme_content = generate_readme_content(notes_by_month, recent_notes, recent_image, pinned_notes)

    # 写入 README.md
    with open("README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)
    print("README.md 更新完成！")


if __name__ == "__main__":
    print("正在扫描笔记...")
    try:
        update_readme()
    except Exception as e:
        print(f"更新失败：{e}")
