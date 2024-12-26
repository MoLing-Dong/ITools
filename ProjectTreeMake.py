import os

"""
这个脚本的功能是生成一个项目的目录树结构，并递归地展示项目的文件夹结构
"""
# 定义需要排除的目录列表
EXCLUDE_DIRS = [".git", ".vscode", ".idea"]
PYTHON_EXCLUDE_DIRS = ["__pycache__", "venv"]
JAVA_EXCLUDE_DIRS = ["target", "out", ".vscode"]
WEB_EXCLUDE_DIRS = ["node_modules", "dist"]

# 合并所有排除目录，使用集合存储，避免重复元素
ALL_EXCLUDE_DIRS = set(EXCLUDE_DIRS + PYTHON_EXCLUDE_DIRS + JAVA_EXCLUDE_DIRS + WEB_EXCLUDE_DIRS)


def generate_tree(directory, indent=""):
    for entry in os.listdir(directory):
        path = os.path.join(directory, entry)
        if os.path.isdir(path):
            # 检查是否需要排除当前目录
            if entry in ALL_EXCLUDE_DIRS:
                continue
            print(f"{indent}├── {entry}/")
            generate_tree(path, indent + "│   ")


if __name__ == "__main__":
    project_path = input("Enter the project directory path: ")
    if os.path.exists(project_path) and os.path.isdir(project_path):
        generate_tree(project_path)
    else:
        print("Invalid directory path!")
