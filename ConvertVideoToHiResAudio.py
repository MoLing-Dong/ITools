import os
import random
import subprocess

from loguru import logger
from pydub import AudioSegment

from ToHiRes import process_directory as enhance_audio_quality  # 导入hires模块的音质提升方法


def weighted_choice(choices):
    """
    根据加权概率随机选择一个元素。
    :param choices: 元素和权重的列表 [(元素, 权重), ...]
    :return: 随机选择的元素
    """
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for item, weight in choices:
        if upto + weight >= r:
            return item
        upto += weight
    return choices[-1][0]  # 如果没有命中，返回最后一个


def generate_chinese_name() -> str:
    """
    随机生成一个三字中文歌曲名称，增强随机性。
    :return: 三字中文歌曲名称
    """
    words = [("巍峨", 2), ("峻峭", 1.9), ("雄浑", 1.8), ("广袤", 1.7), ("缥缈", 1.9), ("阴森", 1.6), ("浩渺", 1.8),
             ("幽僻", 1.5),
             ("峰峦", 1.7), ("山涧", 1.6), ("湖泊", 1.7), ("溪流", 1.6), ("沼泽", 1.5), ("旷野", 1.4), ("山岗", 1.3),
             ("山巅", 1.4),
             ("险嶂", 1.3), ("洼地", 1.2), ("深渊", 1.1), ("礁石", 1.0), ("霹雳", 1.6), ("暴雪", 1.5), ("晨霜", 1.4),
             ("朝露", 1.3),
             ("暮霭", 1.2), ("惊澜", 1.5), ("涟漪", 1.4), ("沙砾", 1.1), ("峭壁", 1.2)]

    # 使用加权选择
    first_char = weighted_choice(words)
    second_char, third_char = random.sample([w for w, _ in words], 2)  # 防止重复

    # 随机选择格式
    patterns = [
        f"{first_char}{second_char}的{third_char}",
        f"{first_char}与{second_char}{third_char}",
        f"{second_char}中{second_char}{third_char}",
        f"{first_char}{second_char}{third_char}",
    ]
    return random.choice(patterns)


def extract_audio_from_video(video_path: str, output_dir: str) -> str | None:
    """
    从视频文件提取音频并保存为 WAV 格式。
    :param video_path: 输入视频文件的路径
    :param output_dir: 提取的音频存放目录
    :return: 提取的音频文件路径
    """
    audio_output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(video_path))[0]}.wav")
    try:
        command = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_output_path, "-y"]
        subprocess.run(command, check=True)
        logger.info(f"提取音频完成: {audio_output_path}")
        return audio_output_path
    except subprocess.CalledProcessError as e:
        logger.error(f"提取音频失败: {video_path}，错误信息: {e}")
        return None


def cut_audio(audio_path: str, output_dir: str) -> list:
    """
    使用 pydub 将音频文件分割成多个随机时长的片段，并返回所有片段的路径列表。
    :param audio_path: 输入音频文件的路径
    :param output_dir: 分割后音频片段的存放目录
    :return: 包含所有音频片段路径的列表
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        duration = len(audio)

        audio_segment_paths = []
        start = 0
        while start < duration:
            segment_duration = random.randint(70 * 1000, 75 * 1000)
            end = min(start + segment_duration, duration)
            audio_segment = audio[start:end]

            segment_filename = f"{generate_chinese_name()}.wav"
            audio_output_path = os.path.join(output_dir, segment_filename)
            audio_segment.export(audio_output_path, format="wav")
            logger.info(f"剪切音频片段完成: {audio_output_path}")

            audio_segment_paths.append(audio_output_path)
            start = end

        return audio_segment_paths
    except Exception as e:
        logger.error(f"音频分割失败: {audio_path}，错误信息: {e}")
        return []


def process_file(input_path: str, output_base_dir: str) -> None:
    """
    根据输入文件类型（音频或视频）进行处理。
    :param input_path: 输入文件的路径
    :param output_base_dir: 输出的基础目录
    """
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    extracted_audio_dir = os.path.join(output_base_dir, "extracted_audio", name)
    audio_output_dir = os.path.join(output_base_dir, "audio_segments", name)
    enhanced_audio_dir = os.path.join(output_base_dir, "enhanced_audio", name)

    os.makedirs(extracted_audio_dir, exist_ok=True)
    os.makedirs(audio_output_dir, exist_ok=True)
    os.makedirs(enhanced_audio_dir, exist_ok=True)

    if ext in (".mp4", ".avi", ".mov", ".mkv"):
        logger.info(f"处理视频文件: {input_path}")
        audio_path = extract_audio_from_video(input_path, extracted_audio_dir)
        if audio_path:
            cut_audio(audio_path, audio_output_dir)
    elif ext in (".wav", ".mp3", ".flac", ".aac"):
        logger.info(f"处理音频文件: {input_path}")
        cut_audio(input_path, audio_output_dir)
    else:
        logger.warning(f"不支持的文件类型: {input_path}")
        return

    enhance_audio_quality(audio_output_dir, enhanced_audio_dir)
    logger.info(f"{name} 的处理完成，音质提升已保存至: {enhanced_audio_dir}")


def process_directory(input_dir: str, output_base_dir: str) -> None:
    """
    遍历目录，处理所有音频和视频文件。
    :param input_dir: 输入目录
    :param output_base_dir: 输出目录
    """
    os.makedirs(output_base_dir, exist_ok=True)
    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        if os.path.isfile(file_path):
            process_file(file_path, output_base_dir)


if __name__ == "__main__":
    input_dir = r'./data'  # 输入文件所在目录
    output_dir = r'./output'  # 处理后的文件存放目录
    process_directory(input_dir, output_dir)
