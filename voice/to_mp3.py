import os
import subprocess
import sys
import platform
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


def check_ffmpeg_installed() -> bool:
    """
    检测系统是否安装了 FFmpeg
    :return: True 如果 FFmpeg 可用，否则 False
    """
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def install_ffmpeg() -> bool:
    """
    根据操作系统自动安装 FFmpeg
    :return: True 如果安装成功，否则 False
    """
    system = platform.system().lower()
    logger.info(f"检测到操作系统: {system}")

    try:
        if system == "linux":
            # 检测 Linux 发行版
            if os.path.exists("/etc/debian_version"):
                logger.info("使用 apt 安装 FFmpeg...")
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(
                    ["sudo", "apt-get", "install", "-y", "ffmpeg"], check=True
                )
            elif os.path.exists("/etc/redhat-release"):
                logger.info("使用 yum 安装 FFmpeg...")
                subprocess.run(["sudo", "yum", "install", "-y", "ffmpeg"], check=True)
            elif os.path.exists("/etc/arch-release"):
                logger.info("使用 pacman 安装 FFmpeg...")
                subprocess.run(
                    ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"], check=True
                )
            else:
                logger.error("未识别的 Linux 发行版，请手动安装 FFmpeg")
                return False

        elif system == "darwin":  # macOS
            logger.info("使用 Homebrew 安装 FFmpeg...")
            brew_check = subprocess.run(["which", "brew"], capture_output=True)
            if brew_check.returncode != 0:
                logger.error(
                    '未安装 Homebrew，请先安装: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                )
                return False
            subprocess.run(["brew", "install", "ffmpeg"], check=True)

        elif system == "windows":
            logger.warning("Windows 系统暂不支持自动安装")
            logger.info("请访问 https://ffmpeg.org/download.html 下载 FFmpeg")
            logger.info("或使用 Chocolatey 安装: choco install ffmpeg")
            return False

        else:
            logger.error(f"不支持的操作系统: {system}")
            return False

        # 验证安装是否成功
        if check_ffmpeg_installed():
            logger.info("FFmpeg 安装成功！")
            return True
        else:
            logger.error("FFmpeg 安装失败，请手动安装")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"安装 FFmpeg 时出错: {e}")
        return False
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return False


def ensure_ffmpeg() -> None:
    """
    确保 FFmpeg 可用，如果不可用则尝试安装
    """
    if check_ffmpeg_installed():
        logger.info("FFmpeg 已安装 ✓")
        return

    logger.warning("未检测到 FFmpeg，准备自动安装...")
    if not install_ffmpeg():
        logger.error("FFmpeg 安装失败，程序无法继续运行")
        sys.exit(1)


def find_ffmpeg() -> str:
    """
    查找可用的 FFmpeg 路径，优先使用系统 FFmpeg，如果不可用，则尝试使用本地 ffmpeg 可执行文件。
    """
    # 检查系统是否安装了 ffmpeg
    if (
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).returncode
        == 0
    ):
        return "ffmpeg"

    # 尝试使用本地 ffmpeg
    local_ffmpeg = "./utils/ffmpeg"
    if os.path.exists(local_ffmpeg) and os.access(local_ffmpeg, os.X_OK):
        return local_ffmpeg

    # 如果都找不到，抛出异常
    raise FileNotFoundError(
        "未找到可用的 FFmpeg，请安装 FFmpeg 或将其放入 utils 目录。"
    )


def convert_audio_to_mp3(input_path: str, output_path: str, ffmpeg_path: str) -> None:
    """
    使用 FFmpeg 将音频文件转换为 MP3 文件。

    :param input_path: 输入音频文件的路径 (MP3 或 WAV)
    :param output_path: 转换后的 MP3 文件的输出路径
    :param ffmpeg_path: FFmpeg 可执行文件路径
    """
    command = [
        ffmpeg_path,
        "-i",
        input_path,  # 输入文件
        "-acodec",
        "mp3",  # 使用 MP3 编码 (替代 libmp3lame)
        "-q:a",
        "2",  # 设置 MP3 的质量 (0-9, 0 是最高质量)
        output_path,  # 输出文件
    ]

    try:
        # 指定 encoding='utf-8' 来解决编码问题
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        logger.info(f"转换完成: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 转换失败: {input_path}，错误信息: {e.stderr or e.stdout}")


def process_directory(
    all_audio_input_dir: str, output_dir: str, max_workers: int = 4
) -> None:
    """
    遍历指定目录，处理所有音频文件，调用转换函数将其转为 MP3 格式。

    :param all_audio_input_dir: 包含音频文件的输入目录
    :param output_dir: 转换后的 MP3 文件的输出目录
    :param max_workers: 线程池最大工作线程数
    """
    # 检查输入目录是否存在
    if not os.path.exists(all_audio_input_dir):
        logger.error(f"输入目录不存在: {all_audio_input_dir}")
        logger.info("请创建目录或输入正确的目录路径")
        return

    if not os.path.isdir(all_audio_input_dir):
        logger.error(f"输入路径不是目录: {all_audio_input_dir}")
        return

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 搜索目录中的 MP3 和 WAV 文件
    audio_files = [
        f for f in os.listdir(all_audio_input_dir) if f.endswith((".mp3", ".wav"))
    ]
    if not audio_files:
        logger.warning(f"目录中没有找到音频文件 (.mp3 或 .wav): {all_audio_input_dir}")
        return

    logger.info(f"找到 {len(audio_files)} 个音频文件，开始转换为 MP3...")

    # 查找可用的 FFmpeg
    try:
        ffmpeg_path = find_ffmpeg()
    except FileNotFoundError as e:
        logger.error(e)
        return

    # 使用多线程处理音频文件的转换
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for filename in audio_files:
            input_path = os.path.join(all_audio_input_dir, filename)
            output_filename = (
                os.path.splitext(filename)[0] + ".mp3"
            )  # 仅修改扩展名为 .mp3
            output_path = os.path.join(output_dir, output_filename)
            executor.submit(convert_audio_to_mp3, input_path, output_path, ffmpeg_path)

    logger.info("所有音频转换完成！")


if __name__ == "__main__":
    # 首先检测并确保 FFmpeg 已安装
    ensure_ffmpeg()

    input_dir = input("请输入音频文件所在的目录: ").strip()
    output_dir = input("请输入转换后的 MP3 文件存放目录: ").strip()
    process_directory(input_dir, output_dir, max_workers=4)
