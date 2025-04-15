import os
import re
from datetime import datetime, timedelta
import shutil


def get_all_notes(directory="notes"):
    """
    扫描指定目录下的所有 Markdown 文件，并按修改时间排序返回文件路径列表。
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"指定的目录不存在: {directory}")

    notes = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                notes.append(os.path.join(root, file))
    notes.sort(key=os.path.getmtime, reverse=True)  # 按修改时间从新到旧排序
    return notes


def get_notes_by_month(notes):
    """
    按年月分类笔记，例如 202504。
    返回一个字典，键为年月（如 202504），值为对应笔记路径列表。
    """
    notes_by_month = {}
    for note in notes:
        mod_time = datetime.fromtimestamp(os.path.getmtime(note))
        year_month = mod_time.strftime("%Y%m")
        if year_month not in notes_by_month:
            notes_by_month[year_month] = []
        notes_by_month[year_month].append(note)
    return notes_by_month


def get_recent_notes(notes, days=7):
    """
    获取最近 N 天内的笔记。
    """
    recent_notes = []
    now = datetime.now()
    cutoff_date = now - timedelta(days=days)
    for note in notes:
        mod_time = datetime.fromtimestamp(os.path.getmtime(note))
        if mod_time >= cutoff_date:
            recent_notes.append(note)
    return recent_notes


def extract_first_image(note_path):
    """
    从笔记中提取第一张图片的路径（如果有）。
    图片格式支持：![](image_url) 或 ![alt_text](image_url)
    """
    with open(note_path, "r", encoding="utf-8") as file:
        content = file.read()
    # 查找图片链接的正则表达式
    match = re.search(r"!\[.*?\]\((.*?)\)", content)
    if match:
        return match.group(1)  # 返回图片路径
    return None


def generate_readme(notes_by_month, recent_notes, recent_image):
    """
    根据分类、最近笔记和最近一篇有插图的笔记生成 README 内容。
    """
    readme_content = "# 笔记目录\n\n"

    # 添加最近更新时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content += f"**最近更新时间：{now}**\n\n"

    # 添加最近一篇有插图笔记的第一张插图
    if recent_image:
        readme_content += f"![最近插图]({recent_image})\n\n"

    # 最近 7 天的笔记
    readme_content += "## 最近 7 天的笔记\n\n"
    for note in recent_notes:
        note_name = os.path.basename(note)
        readme_content += f"- [{note_name}]({note})\n"
    readme_content += "\n"

    # 按年月分类笔记
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
    主函数，扫描笔记目录并更新 README.md 文件。
    """
    notes_dir = "notes"  # 笔记目录
    notes = get_all_notes(notes_dir)  # 获取所有笔记
    notes_by_month = get_notes_by_month(notes)  # 按年月分类笔记
    recent_notes = get_recent_notes(notes)  # 获取最近 7 天的笔记

    # 提取最近一篇有插图笔记的第一张插图
    recent_image = None
    for note in notes:
        recent_image = extract_first_image(note)
        if recent_image:
            break

    # 生成 README 内容
    readme_content = generate_readme(notes_by_month, recent_notes, recent_image)

    # 写入 README.md
    readme_path = "README.md"
    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(readme_content)
    print(f"README.md 更新完成！")


if __name__ == "__main__":
    print("正在扫描文章...")
    try:
        update_readme()
    except Exception as e:
        print(f"更新失败：{e}")
