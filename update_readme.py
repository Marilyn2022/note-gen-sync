import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

# 项目目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.path.join(BASE_DIR, "notes")  # 假设笔记存放在 notes 文件夹中

def get_all_notes():
    """获取所有 .md 文件路径"""
    notes = []
    for root, _, files in os.walk(NOTES_DIR):
        for file in files:
            if file.endswith(".md"):
                notes.append(os.path.join(root, file))
    return notes

def get_note_metadata(note_path):
    """获取笔记的元数据"""
    with open(note_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    title = lines[0].strip() if lines else "无标题"
    is_pinned = "置顶" in title
    image_path = None
    for line in lines:
        match = re.search(r'!\[.*?\]\((.*?)\)', line)
        if match:
            image_path = match.group(1)
            break
    return {
        "path": note_path,
        "title": title,
        "is_pinned": is_pinned,
        "image": image_path,
        "last_modified": datetime.fromtimestamp(os.path.getmtime(note_path))
    }

def generate_readme():
    """生成 README 文件"""
    notes = get_all_notes()
    notes_metadata = [get_note_metadata(note) for note in notes]

    # 目录
    directory = "## 笔记目录\n"
    for meta in notes_metadata:
        relative_path = os.path.relpath(meta['path'], BASE_DIR)
        directory += f"- [{meta['title']}]({relative_path})\n"

    # 最近更新时间
    latest_note = max(notes_metadata, key=lambda x: x['last_modified'])
    last_update = f"## 最近更新时间\n- 最新更新: [{latest_note['title']}]({os.path.relpath(latest_note['path'], BASE_DIR)}) - {latest_note['last_modified']}\n"

    # 最近 7 天的笔记
    recent_notes = [
        meta for meta in notes_metadata
        if meta['last_modified'] >= datetime.now() - timedelta(days=7)
    ]
    recent_notes_section = "## 最近 7 天的笔记\n"
    for meta in recent_notes:
        recent_notes_section += f"- [{meta['title']}]({os.path.relpath(meta['path'], BASE_DIR)})\n"

    # 按年月分类
    notes_by_year_month = defaultdict(list)
    for meta in notes_metadata:
        year_month = meta['last_modified'].strftime("%Y-%m")
        notes_by_year_month[year_month].append(meta)
    year_month_section = "## 按年月分类笔记\n"
    for year_month, metas in notes_by_year_month.items():
        year_month_section += f"### {year_month}\n"
        for meta in metas:
            year_month_section += f"- [{meta['title']}]({os.path.relpath(meta['path'], BASE_DIR)})\n"

    # 笔记关联内容（简单实现为同目录下的其他笔记）
    related_notes_section = "## 笔记关联内容\n"
    for meta in notes_metadata:
        related_notes_section += f"### {meta['title']}\n"
        related_notes_section += "关联笔记:\n"
        related_notes = [
            other_meta for other_meta in notes_metadata
            if os.path.dirname(other_meta['path']) == os.path.dirname(meta['path'])
            and other_meta['path'] != meta['path']
        ]
        for related in related_notes:
            related_notes_section += f"- [{related['title']}]({os.path.relpath(related['path'], BASE_DIR)})\n"
    
    # 置顶笔记
    pinned_notes = [meta for meta in notes_metadata if meta['is_pinned']]
    pinned_section = "## 置顶笔记\n"
    for meta in pinned_notes:
        pinned_section += f"- [{meta['title']}]({os.path.relpath(meta['path'], BASE_DIR)})\n"

    # 合并所有部分
    readme_content = (
        "# 笔记汇总\n\n" +
        directory + "\n" +
        last_update + "\n" +
        pinned_section + "\n" +
        recent_notes_section + "\n" +
        year_month_section + "\n" +
        related_notes_section
    )

    # 写入 README.md 文件
    with open(os.path.join(BASE_DIR, "README.md"), 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == "__main__":
    generate_readme()
