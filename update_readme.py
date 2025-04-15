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


def generate_readme_content(notes_by_month, recent_notes, recent_image):
    """
    根据笔记分类、最近笔记和最近插图生成 README 内容。
    """
    readme_content = "# 笔记目录\n\n"

    # 最近更新时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content += f"**最近更新时间：{now}**\n\n"

    # 最近的插图
    if recent_image:
        readme_content += f"![最近插图]({recent_image})\n\n"

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
    recent_image = find_first_image_in_notes(notes)

    # 生成 README 内容
    readme_content = generate_readme_content(notes_by_month, recent_notes, recent_image)

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
