import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


def convert_mp3_to_wav(input_path: str, output_path: str) -> None:
    """
    使用 FFmpeg 将 MP3 转换为 WAV 文件，并确保采样率为 384kHz，采样位深为 16bit。

    :param input_path: MP3 文件的输入路径
    :param output_path: 转换后的 WAV 文件的输出路径
    """
    command = [
        'ffmpeg', '-i', input_path,  # 输入文件
        '-ar', '96000',  # 采样率 96kHz
        '-ac', '2',  # 双声道
        '-sample_fmt', 's32',  # 32bit 位深度
        '-acodec', 'pcm_s32le',  # 使用 32 位的 PCM 编码
        output_path  # 输出文件
    ]

    try:
        # 指定编码为 utf-8 以避免编码错误
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                encoding='utf-8')
        print(f"转换完成: {output_path}")
        print(result.stdout)  # 输出 FFmpeg 的信息
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {input_path}，错误信息: {e}")
        print(e.stderr)  # 打印 FFmpeg 错误信息


def process_directory(input_dir: str, output_dir: str) -> None:
    """
    遍历指定目录，处理所有 MP3 文件，调用转换函数将其转为 WAV 格式。

    :param input_dir: 包含 MP3 文件的输入目录
    :param output_dir: 转换后的 WAV 文件的输出目录
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 搜索目录中的 MP3 文件
    mp3_files = [f for f in os.listdir(input_dir) if f.endswith(".mp3")]
    if not mp3_files:
        print("目录中没有找到 MP3 文件。")
        return

    # 使用多线程处理 MP3 文件的转换
    with ThreadPoolExecutor() as executor:
        for filename in mp3_files:
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.wav'  # 保持原文件名，仅修改扩展名为 .wav
            output_path = os.path.join(output_dir, output_filename)
            executor.submit(convert_mp3_to_wav, input_path, output_path)


if __name__ == "__main__":
    # 定义要转换的目录
    input_dir = r'D:\ProjectForStudent\ITools'  # MP3 文件所在的目录
    output_dir = r'D:\ProjectForStudent\ITools\output'  # 转换后的 WAV 文件存放目录

    process_directory(input_dir, output_dir)
