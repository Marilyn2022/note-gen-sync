import os
import re
from datetime import datetime

# 获取最新有插图文章的第一张图片
def get_first_image_from_latest_article(notes):
    """
    从所有文章中查找最新有插图的文章，并返回其第一张图片的 URL。
    """
    for note in sorted(notes, key=lambda x: os.path.getmtime(x), reverse=True):
        try:
            with open(note, "r", encoding="utf-8") as f:
                content = f.read()
                # 查找图片链接格式 ![alt](url)
                match = re.search(r"!\[.*?\]\((.*?)\)", content)
                if match:
                    return match.group(1)  # 返回第一张图片的 URL
        except (FileNotFoundError, IOError) as e:
            print(f"无法读取文件 {note}：{e}")
    return None  # 如果没有找到，返回 None

# 修改生成 README.md 的函数
def generate_readme_content(note_structure, recent_notes, latest_image_url):
    """
    生成 README.md 文件的内容，包括最新文章、按年月分类的文章目录以及最新文章中的图片。
    """
    readme_content = "# 笔记目录\n\n"
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    readme_content += f"**最后更新：{current_date}**\n\n"
    
    # 显示最新有插图文章的第一张图片
    if latest_image_url:
        readme_content += f"![最新文章图片]({latest_image_url})\n\n"

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

# 更新 README 文件
def update_readme(project_directory, content):
    """
    将内容写入 README.md 文件。
    """
    readme_path = os.path.join(project_directory, "README.md")
    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"README.md 已成功更新！路径：{readme_path}")
    except (FileNotFoundError, IOError) as e:
        print(f"写入 README.md 文件失败：{e}")

# 修改主程序
def main():
    """
    主程序入口，扫描文章目录，生成 README.md 文件。
    """
    project_directory = "."  # 当前目录
    print("正在扫描文章...")

    # 获取所有文章
    try:
        notes = get_all_notes(project_directory)
        print(f"发现 {len(notes)} 篇文章。")
    except Exception as e:
        print(f"获取文章失败：{e}")
        return

    # 按年月分类
    note_structure = organize_notes_by_year_month(notes)

    # 获取最近一周的更新
    recent_notes = get_recent_notes(notes)
    print(f"最近一周有 {len(recent_notes)} 篇更新。")

    # 获取最新有插图文章的第一张图片
    latest_image_url = get_first_image_from_latest_article(notes)
    if latest_image_url:
        print(f"找到最新文章的图片：{latest_image_url}")
    else:
        print("未找到含图片的文章。")

    # 生成 README.md 内容
    readme_content = generate_readme_content(note_structure, recent_notes, latest_image_url)

    # 更新 README.md 文件
    update_readme(project_directory, readme_content)

if __name__ == "__main__":
    main()
