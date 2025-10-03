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


def convert_audio_to_wav(input_path: str, output_path: str) -> None:
    """
    使用 FFmpeg 将音频文件转换为 WAV 文件，并确保采样率为 96000Hz，采样位深为 32bit。

    :param input_path: 输入音频文件的路径 (MP3 或 WAV)
    :param output_path: 转换后的 WAV 文件的输出路径
    """
    # 尝试使用系统 FFmpeg
    command = [
        "ffmpeg",
        "-i",
        input_path,  # 输入文件
        "-ar",
        "96000",  # 采样率 96000Hz
        "-ac",
        "2",  # 双声道
        "-sample_fmt",
        "s32",  # 32bit 位深度
        "-acodec",
        "pcm_s32le",  # 使用 32 位的 PCM 编码
        output_path,  # 输出文件
    ]

    try:
        # 尝试运行系统的 ffmpeg
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="ignore",
        )
        logger.info(f"转换完成: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.info(f"系统 FFmpeg 转换失败: {input_path}，尝试使用本地 FFmpeg")
        # 尝试使用当前目录下的 ffmpeg
        local_ffmpeg = "./utils/ffmpeg"  # 假设 ffmpeg 在当前目录下的 utils 文件夹
        command[0] = local_ffmpeg  # 替换为本地的 ffmpeg 可执行文件路径
        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                errors="ignore",
            )
            logger.info(f"本地 FFmpeg 转换完成: {output_path}")
            logger.info(result.stdout)  # 输出 FFmpeg 的信息
        except subprocess.CalledProcessError as e:
            logger.info(f"本地 FFmpeg 转换仍然失败: {input_path}，错误信息: {e}")
            logger.info(e.stderr)  # 打印 FFmpeg 错误信息


def process_directory(all_audio_input_dir: str, output_dir: str) -> None:
    """
    遍历指定目录，处理所有音频文件，调用转换函数将其转为 WAV 格式。

    :param all_audio_input_dir: 包含音频文件的输入目录
    :param output_dir: 转换后的 WAV 文件的输出目录
    """
    # 检查输入目录是否存在
    if not os.path.exists(all_audio_input_dir):
        logger.error(f"输入目录不存在: {all_audio_input_dir}")
        logger.info("请创建目录或修改代码中的 input_dir 路径")
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

    logger.info(f"找到 {len(audio_files)} 个音频文件，开始转换...")

    # 使用多线程处理音频文件的转换
    with ThreadPoolExecutor() as executor:
        for filename in audio_files:
            input_path = os.path.join(all_audio_input_dir, filename)
            output_filename = (
                os.path.splitext(filename)[0] + ".wav"
            )  # 保持原文件名，仅修改扩展名为 .wav
            output_path = os.path.join(output_dir, output_filename)
            executor.submit(convert_audio_to_wav, input_path, output_path)

    logger.info("所有音频转换完成！")


if __name__ == "__main__":
    # 首先检测并确保 FFmpeg 已安装
    ensure_ffmpeg()

    # 定义要转换的目录
    input_dir = r"./data"  # 音频文件所在的目录
    output_dir = r"./output"  # 转换后的 WAV 文件存放目录
    process_directory(input_dir, output_dir)
