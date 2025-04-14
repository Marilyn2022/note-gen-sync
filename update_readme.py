import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

# 获取当前项目中的所有 .md 文件
def get_all_notes(directory):
    notes = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md") and file != "README.md":
                file_path = os.path.join(root, file)
                notes.append(file_path)
    return notes

# 按年月 (YYYYMM) 分类
def organize_notes_by_year_month(notes):
    note_structure = defaultdict(list)
    date_pattern = re.compile(r"(\d{4})(\d{2})")  # 匹配 YYYYMM 格式

    for note in notes:
        file_name = os.path.basename(note)
        match = date_pattern.match(file_name)
        if match:
            year_month = f"{match.group(1)}/{match.group(2)}"
            note_structure[year_month].append(note)

    return note_structure

# 获取最近一周的更新
def get_recent_notes(notes):
    recent_notes = []
    one_week_ago = datetime.now() - timedelta(days=7)

    for note in notes:
        file_time = datetime.fromtimestamp(os.path.getmtime(note))
        if file_time >= one_week_ago:
            recent_notes.append((file_time, note))

    # 按更新时间排序
    recent_notes.sort(reverse=True, key=lambda x: x[0])
    return [note for _, note in recent_notes]

# 生成 README.md 的内容
def generate_readme_content(note_structure, recent_notes):
    readme_content = "# 笔记目录\n\n"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content += f"**最后更新：{current_date}**\n\n"

    # 最新文章
    if recent_notes:
        readme_content += "## 最新文章\n\n"
        for note in recent_notes:
            relative_path = os.path.relpath(note, ".")
            file_name = os.path.basename(note)
            readme_content += f"- [{file_name}]({relative_path})\n"
        readme_content += "\n"

    # 按年月分类
    for year_month, notes in sorted(note_structure.items(), reverse=True):
        readme_content += f"## {year_month}\n\n"
        for note in sorted(notes):
            relative_path = os.path.relpath(note, ".")
            file_name = os.path.basename(note)
            readme_content += f"- [{file_name}]({relative_path})\n"
        readme_content += "\n"

    return readme_content

# 写入 README.md
def update_readme(directory, readme_content):
    readme_path = os.path.join(directory, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

# 主程序
def main():
    project_directory = "."  # 当前目录
    print("正在扫描文章...")
    
    # 获取所有文章
    notes = get_all_notes(project_directory)
    print(f"发现 {len(notes)} 篇文章。")

    # 按年月分类
    note_structure = organize_notes_by_year_month(notes)

    # 获取最近一周的更新
    recent_notes = get_recent_notes(notes)
    print(f"最近一周有 {len(recent_notes)} 篇更新。")

    # 生成 README.md 内容
    readme_content = generate_readme_content(note_structure, recent_notes)

    # 更新 README.md 文件
    update_readme(project_directory, readme_content)
    print("README.md 已成功更新！")

if __name__ == "__main__":
    main()