import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

"""
把 MP3 或 WAV 文件转换为 WAV 文件，并确保采样率为 384kHz，采样位深为 32bit。
"""


def convert_audio_to_wav(input_path: str, output_path: str) -> None:
    """
    使用 FFmpeg 将音频文件转换为 WAV 文件，并确保采样率为 384kHz，采样位深为 32bit。

    :param input_path: 输入音频文件的路径 (MP3 或 WAV)
    :param output_path: 转换后的 WAV 文件的输出路径
    """
    command = [
        'ffmpeg', '-i', input_path,  # 输入文件
        '-ar', '192000',  # 采样率 384kHz
        '-ac', '2',  # 双声道
        '-sample_fmt', 's32',  # 32bit 位深度
        '-acodec', 'pcm_s32le',  # 使用 32 位的 PCM 编码
        output_path  # 输出文件
    ]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                errors='ignore')
        print(f"转换完成: {output_path}")
        print(result.stdout)  # 输出 FFmpeg 的信息
    except subprocess.CalledProcessError as e:
        print(f"转换失败: {input_path}，错误信息: {e}")
        print(e.stderr)  # 打印 FFmpeg 错误信息


def process_directory(all_audio_input_dir: str, output_dir: str) -> None:
    """
    遍历指定目录，处理所有音频文件，调用转换函数将其转为 WAV 格式。

    :param all_audio_input_dir: 包含音频文件的输入目录
    :param output_dir: 转换后的 WAV 文件的输出目录
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 搜索目录中的 MP3 和 WAV 文件
    audio_files = [f for f in os.listdir(all_audio_input_dir) if f.endswith((".mp3", ".wav"))]
    if not audio_files:
        print("目录中没有找到音频文件。")
        return

    # 使用多线程处理音频文件的转换
    with ThreadPoolExecutor() as executor:
        for filename in audio_files:
            input_path = os.path.join(all_audio_input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.wav'  # 保持原文件名，仅修改扩展名为 .wav
            output_path = os.path.join(output_dir, output_filename)
            executor.submit(convert_audio_to_wav, input_path, output_path)


if __name__ == "__main__":
    # 定义要转换的目录
    input_dir = r'./data'  # 音频文件所在的目录
    output_dir = r'./output'  # 转换后的 WAV 文件存放目录
    process_directory(input_dir, output_dir)
