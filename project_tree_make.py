import os

"""
这个脚本的功能是生成一个项目的目录树结构，并递归地展示项目的文件夹结构
"""
# 定义需要排除的目录列表
EXCLUDE_DIRS = [".git", ".vscode", ".idea"]
PYTHON_EXCLUDE_DIRS = ["__pycache__", ".venv"]
JAVA_EXCLUDE_DIRS = ["target", "out", ".vscode"]
WEB_EXCLUDE_DIRS = ["node_modules", "dist"]

# 合并所有排除目录，使用集合存储，避免重复元素
ALL_EXCLUDE_DIRS = set(EXCLUDE_DIRS + PYTHON_EXCLUDE_DIRS + JAVA_EXCLUDE_DIRS + WEB_EXCLUDE_DIRS)


def generate_tree(directory, indent=""):
    # 获取当前目录下的所有目录项
    items = [entry for entry in os.listdir(directory) if os.path.isdir(os.path.join(directory, entry))]
    # 过滤掉需要排除的目录
    valid_items = [item for item in items if item not in ALL_EXCLUDE_DIRS]
    for index, entry in enumerate(valid_items):
        path = os.path.join(directory, entry)
        # 判断是否为最后一个目录
        if index == len(valid_items) - 1:
            print(f"{indent}└── {entry}/")
            new_indent = indent + "    "
        else:
            print(f"{indent}├── {entry}/")
            new_indent = indent + "│   "
        generate_tree(path, new_indent)


if __name__ == "__main__":
    project_path = input("Enter the project directory path: ")
    if os.path.exists(project_path) and os.path.isdir(project_path):
        # 先打印当前文件夹名(project_path) 只要最后的文件夹的名字
        print(f"{os.path.basename(project_path)}")
        generate_tree(project_path)
    else:
        print("Invalid directory path!")