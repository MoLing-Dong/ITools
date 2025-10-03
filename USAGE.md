# 使用说明

## 项目结构

这个项目包含三个主要的音视频处理工具：

### 1. ConvertVideoToHiResAudio.py - 视频/音频转高清音频

**功能：**

- 从视频中提取音频
- 将音频切割成随机时长片段（70-75秒）
- 提升音频质量（96kHz, 32bit）
- 生成随机中文文件名

**使用方法：**

```bash
# 1. 将视频或音频文件放入 data 目录
mkdir -p data
# 复制你的视频文件（.mp4, .avi, .mov, .mkv）或音频文件（.wav, .mp3, .flac, .aac）到 data/

# 2. 运行脚本
uv run python ConvertVideoToHiResAudio.py

# 3. 结果会保存在 output/ 目录下
# - output/extracted_audio/: 从视频提取的原始音频
# - output/audio_segments/: 切割后的音频片段
# - output/enhanced_audio/: 音质提升后的最终音频
```

### 2. ToHiRes.py - 音频转高清格式

**功能：**

- 将音频文件转换为高质量 WAV 格式
- 采样率：96000Hz
- 声道：立体声（2 声道）
- 位深：32bit

**使用方法：**

```bash
# 1. 将音频文件放入 data 目录
mkdir -p data
# 复制 .mp3 或 .wav 文件到 data/

# 2. 运行脚本
uv run python ToHiRes.py

# 3. 转换后的高清 WAV 文件会保存在 output/ 目录
```

### 3. ToMp3.py - 音频转 MP3 格式

**功能：**

- 将音频文件转换为高质量 MP3 格式
- 质量等级：2（接近最高质量）

**使用方法：**

```bash
# 运行脚本（会提示输入目录）
uv run python ToMp3.py

# 根据提示输入：
# - 输入音频文件所在的目录（如：./data）
# - 输入转换后的 MP3 文件存放目录（如：./output）
```

## 自动依赖管理

### FFmpeg 自动安装

所有脚本都会自动检测 FFmpeg 是否安装，如果未安装会尝试自动安装：

- **Linux (Debian/Ubuntu)**: 自动使用 `apt-get install ffmpeg`
- **Linux (RedHat/CentOS)**: 自动使用 `yum install ffmpeg`
- **Linux (Arch)**: 自动使用 `pacman -S ffmpeg`
- **macOS**: 自动使用 `brew install ffmpeg`（需要先安装 Homebrew）
- **Windows**: 提供手动安装指引

### Python 依赖

使用 `uv` 管理 Python 依赖：

```bash
# 安装所有依赖
uv sync

# 添加新依赖
uv add package-name

# 运行脚本
uv run python script_name.py
```

## 输出信息说明

运行脚本时会看到以下类型的日志：

- ✅ **INFO** - 正常操作信息（绿色/蓝色）
- ⚠️ **WARNING** - 警告信息（黄色）
- ❌ **ERROR** - 错误信息（红色）

### 常见输出

```
FFmpeg 已安装 ✓                    # FFmpeg 检测成功
找到 3 个文件，开始处理...          # 发现待处理文件
转换完成: output/xxx.wav          # 单个文件处理完成
所有文件处理完成！                 # 全部处理完成
输入目录不存在: ./data            # 目录不存在
输入目录中没有文件: ./data        # 目录为空
```

## 快速开始示例

```bash
# 1. 创建测试目录
mkdir -p data output

# 2. 下载一个测试视频（示例）
# wget -O data/test.mp4 "https://example.com/test-video.mp4"

# 3. 运行转换
uv run python ConvertVideoToHiResAudio.py

# 4. 检查结果
ls -lh output/enhanced_audio/
```

## 注意事项

1. **FFmpeg 依赖**：所有脚本都需要 FFmpeg，首次运行会自动安装
2. **磁盘空间**：处理大文件时需要足够的磁盘空间
3. **多线程处理**：脚本使用多线程加速处理，CPU 占用可能较高
4. **文件格式**：确保输入的文件格式被支持

## 技术细节

- **编程语言**: Python 3.8+
- **主要依赖**:
  - `loguru` - 日志记录
  - `pydub` - 音频处理
  - `FFmpeg` - 音视频编解码（系统依赖）
- **包管理**: `uv`
- **并发处理**: `ThreadPoolExecutor`

## 故障排查

### 问题：找不到 FFmpeg

```
解决：确保 FFmpeg 已正确安装
sudo apt-get install ffmpeg  # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### 问题：目录不存在

```
解决：创建所需目录
mkdir -p data output
```

### 问题：没有找到文件

```
解决：确保文件格式正确
支持的格式：.mp4, .avi, .mov, .mkv, .wav, .mp3, .flac, .aac
```
