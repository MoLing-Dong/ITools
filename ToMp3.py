import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from loguru import logger


def find_ffmpeg() -> str:
    """
    查找可用的 FFmpeg 路径，优先使用系统 FFmpeg，如果不可用，则尝试使用本地 ffmpeg 可执行文件。
    """
    # 检查系统是否安装了 ffmpeg
    if subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0:
        return "ffmpeg"

    # 尝试使用本地 ffmpeg
    local_ffmpeg = "./utils/ffmpeg"
    if os.path.exists(local_ffmpeg) and os.access(local_ffmpeg, os.X_OK):
        return local_ffmpeg

    # 如果都找不到，抛出异常
    raise FileNotFoundError("未找到可用的 FFmpeg，请安装 FFmpeg 或将其放入 utils 目录。")


def convert_audio_to_mp3(input_path: str, output_path: str, ffmpeg_path: str) -> None:
    """
    使用 FFmpeg 将音频文件转换为 MP3 文件。

    :param input_path: 输入音频文件的路径 (MP3 或 WAV)
    :param output_path: 转换后的 MP3 文件的输出路径
    :param ffmpeg_path: FFmpeg 可执行文件路径
    """
    command = [
        ffmpeg_path, '-i', input_path,  # 输入文件
        '-acodec', 'mp3',  # 使用 MP3 编码 (替代 libmp3lame)
        '-q:a', '2',  # 设置 MP3 的质量 (0-9, 0 是最高质量)
        output_path  # 输出文件
    ]

    try:
        # 指定 encoding='utf-8' 来解决编码问题
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        logger.info(f"转换完成: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 转换失败: {input_path}，错误信息: {e.stderr or e.stdout}")


def process_directory(all_audio_input_dir: str, output_dir: str, max_workers: int = 4) -> None:
    """
    遍历指定目录，处理所有音频文件，调用转换函数将其转为 MP3 格式。

    :param all_audio_input_dir: 包含音频文件的输入目录
    :param output_dir: 转换后的 MP3 文件的输出目录
    :param max_workers: 线程池最大工作线程数
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 搜索目录中的 MP3 和 WAV 文件
    audio_files = [f for f in os.listdir(all_audio_input_dir) if f.endswith((".mp3", ".wav"))]
    if not audio_files:
        logger.info("目录中没有找到音频文件。")
        return

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
            output_filename = os.path.splitext(filename)[0] + '.mp3'  # 仅修改扩展名为 .mp3
            output_path = os.path.join(output_dir, output_filename)
            executor.submit(convert_audio_to_mp3, input_path, output_path, ffmpeg_path)


if __name__ == "__main__":
    input_dir = input("请输入音频文件所在的目录: ").strip()
    output_dir = input("请输入转换后的 MP3 文件存放目录: ").strip()
    process_directory(input_dir, output_dir, max_workers=4)