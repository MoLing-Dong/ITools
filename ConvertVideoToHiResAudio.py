import os
import random
import subprocess

from loguru import logger
from pydub import AudioSegment

from ToHiRes import process_directory as enhance_audio_quality  # 导入hires模块的音质提升方法


def generate_chinese_name() -> str:
    """
    随机生成一个三字中文歌曲名称。
    :return: 三字中文歌曲名称
    """
    words = ["梦", "心", "光", "夜", "雨", "风", "星", "海", "月", "花", "雪", "琴", "云", "山", "情", "歌", "泪", "舞",
             "影"]

    # 随机选取三个词并组合
    return ''.join(random.choice(words) for _ in range(3))


def extract_audio_from_video(video_path: str, output_dir: str) -> str | None:
    """
    从视频文件提取音频并保存为 WAV 格式。
    :param video_path: 输入视频文件的路径
    :param output_dir: 提取的音频存放目录
    :return: 提取的音频文件路径
    """
    audio_output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(video_path))[0]}.wav")

    try:
        # 使用 subprocess 调用 ffmpeg 提取音频
        command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_output_path, "-y"]
        subprocess.run(command, check=True)
        logger.info(f"提取音频完成: {audio_output_path}")
        return audio_output_path
    except subprocess.CalledProcessError as e:
        logger.info(f"提取音频失败: {video_path}，错误信息: {e}")
        return None


def cut_audio(audio_path: str, output_dir: str) -> list:
    """
    使用 pydub 将音频文件分割成多个随机时长的片段，并返回所有片段的路径列表。
    :param audio_path: 输入音频文件的路径
    :param output_dir: 分割后音频片段的存放目录
    :return: 包含所有音频片段路径的列表
    """
    try:
        # 使用 pydub 加载音频文件
        audio = AudioSegment.from_wav(audio_path)
        duration = len(audio)  # 获取音频总时长

        audio_segment_paths = []
        start = 0

        # 使用 pydub 逐个切割音频片段
        while start < duration:
            # 在循环内生成新的随机片段时长
            segment_duration = random.randint(180 * 1000, 195 * 1000)
            end = min(start + segment_duration, duration)
            audio_segment = audio[start:end]

            # 生成唯一的文件名
            segment_filename = f"{generate_chinese_name()}.wav"
            audio_output_path = os.path.join(output_dir, segment_filename)
            audio_segment.export(audio_output_path, format="wav")
            logger.info(f"剪切音频片段完成: {audio_output_path}")

            audio_segment_paths.append(audio_output_path)
            start = end  # 更新起始位置为当前片段的结束位置

        return audio_segment_paths
    except Exception as e:
        logger.info(f"音频分割失败: {audio_path}，错误信息: {e}")
        return []


def process_video_directory(video_input_dir: str) -> None:
    """
    遍历指定目录，处理所有视频文件，提取音频并提升音质。
    :param video_input_dir: 包含视频文件的输入目录
    """
    os.makedirs(video_input_dir, exist_ok=True)

    video_files = [f for f in os.listdir(video_input_dir) if f.endswith((".mp4", ".avi", ".mov", ".mkv"))]

    if not video_files:
        logger.info("目录中没有找到视频文件。")
        return

    for filename in video_files:
        video_path = os.path.join(video_input_dir, filename)
        song_name = os.path.splitext(filename)[0]  # 获取当前视频的歌曲名称

        # 创建与歌曲名称对应的目录
        extracted_audio_dir = os.path.join('./extracted_audio', song_name)  # 提取的音频存放目录
        audio_output_dir = os.path.join('./audio_segments', song_name)  # 分割后的音频片段存放目录
        enhanced_audio_dir = os.path.join('./enhanced_audio', song_name)  # 提升后音频的存放目录

        os.makedirs(extracted_audio_dir, exist_ok=True)
        os.makedirs(audio_output_dir, exist_ok=True)
        os.makedirs(enhanced_audio_dir, exist_ok=True)

        # 提取音频
        audio_path = extract_audio_from_video(video_path, extracted_audio_dir)
        if audio_path:
            # 分割提取后的音频
            cut_audio(audio_path, audio_output_dir)

        # 调用hires进行音质提升
        enhance_audio_quality(audio_output_dir, enhanced_audio_dir)
        logger.info(f"{song_name} 的音质提升完成。")


if __name__ == "__main__":
    input_dir = r'./data'  # 视频文件所在的目录
    process_video_directory(input_dir)
