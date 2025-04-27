import os
import re
from datetime import datetime, timedelta


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


def find_pinned_notes(notes):
    """
    检查笔记的第一行标题是否包含"置顶"关键字，返回置顶笔记列表。
    """
    pinned_notes = []
    for note in notes:
        try:
            with open(note, "r", encoding="utf-8") as file:
                first_line = file.readline().strip()
                if "置顶" in first_line and first_line.startswith("#"):
                    pinned_notes.append(note)
        except Exception:
            continue
    return pinned_notes


def extract_keywords_from_note(note_path, max_keywords=5):
    """
    从笔记中提取关键词，用于关联内容匹配。
    简单实现：提取标题中的非停用词作为关键词。
    """
    try:
        with open(note_path, "r", encoding="utf-8") as file:
            content = file.read()
            # 提取标题
            title_match = re.search(r"^#\s+(.*?)$", content, re.MULTILINE)
            if not title_match:
                return []
            
            title = title_match.group(1)
            # 简单的停用词列表
            stop_words = ["的", "了", "和", "与", "或", "在", "是", "有", "被", "将", "把"]
            # 分词并过滤停用词
            words = [word for word in re.findall(r'\w+', title) if len(word) > 1 and word not in stop_words]
            return words[:max_keywords]
    except Exception:
        return []


def find_related_notes(current_note, all_notes, max_related=5):
    """
    根据笔记内容中的关键词，匹配往期关联的笔记。
    """
    if current_note not in all_notes:
        return []
    
    keywords = extract_keywords_from_note(current_note)
    if not keywords:
        return []
    
    related_notes = []
    for note in all_notes:
        if note == current_note:
            continue
        
        try:
            with open(note, "r", encoding="utf-8") as file:
                content = file.read().lower()
                # 计算匹配的关键词数量
                match_count = sum(1 for keyword in keywords if keyword.lower() in content)
                if match_count > 0:
                    related_notes.append((note, match_count))
        except Exception:
            continue
    
    # 按匹配度排序并限制数量
    related_notes.sort(key=lambda x: x[1], reverse=True)
    return [note for note, _ in related_notes[:max_related]]


def update_note_with_related_content(note_path, related_notes):
    """
    在笔记底部添加关联内容链接。
    """
    if not related_notes:
        return
    
    try:
        with open(note_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # 检查是否已经有关联内容部分
        if "## 相关笔记" in content:
            # 已存在关联内容，不重复添加
            return
        
        # 添加关联内容部分
        related_content = "\n\n## 相关笔记\n\n"
        for related_note in related_notes:
            note_name = os.path.basename(related_note)
            related_content += f"- [{note_name}]({related_note})\n"
        
        # 写回文件
        with open(note_path, "w", encoding="utf-8") as file:
            file.write(content + related_content)
    except Exception as e:
        print(f"更新笔记 {note_path} 失败: {e}")


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
            # 读取笔记的第一行作为标题
            try:
                with open(note, "r", encoding="utf-8") as file:
                    first_line = file.readline().strip()
                    # 移除Markdown标题符号和"置顶"关键字
                    title = re.sub(r'^#+\s+', '', first_line).replace("置顶", "").strip()
                    readme_content += f"- [{title}]({note})\n"
            except Exception:
                readme_content += f"- [{note_name}]({note})\n"
        readme_content += "\n"

    # 最近 7 天的笔记
    readme_content += "## 🕒 最近 7 天的笔记\n\n"
    for note in recent_notes:
        note_name = os.path.basename(note)
        readme_content += f"- [{note_name}]({note})\n"
    readme_content += "\n"

    # 按年月分类的笔记
    readme_content += "## 📅 按年月分类的笔记\n\n"
    # 按年月排序
    sorted_months = sorted(notes_by_month.keys(), reverse=True)
    for year_month in sorted_months:
        # 格式化显示，如"2023年05月"
        year = year_month[:4]
        month = year_month[4:]
        formatted_month = f"{year}年{month}月"
        readme_content += f"### {formatted_month}\n\n"
        for note in notes_by_month[year_month]:
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
    recent_image = find_first_image_in_notes(notes)
    pinned_notes = find_pinned_notes(notes)
    
    # 为每个笔记添加关联内容
    for note in notes:
        related_notes = find_related_notes(note, notes)
        if related_notes:
            update_note_with_related_content(note, related_notes)

    # 生成 README 内容
    readme_content = generate_readme_content(notes_by_month, recent_notes, recent_image, pinned_notes)

    # 写入 README.md
    with open("README.md", "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)
    print("README.md 更新完成！")
    print(f"共处理 {len(notes)} 篇笔记，其中置顶笔记 {len(pinned_notes)} 篇，最近更新 {len(recent_notes)} 篇")


if __name__ == "__main__":
    print("正在扫描笔记...")
    try:
        update_readme()
    except Exception as e:
        print(f"更新失败：{e}")
