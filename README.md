# 📚 StudyTimelapse: Automated Productivity Tracker

A Python-based automation tool designed to document study sessions by capturing periodic frames, overlaying real-time media metadata, and auto-compiling the results into a high-efficiency timelapse video.

## 🌟 Key Features
- **Automated Capture:** Intelligent frame-grabbing at user-defined intervals (default 10s).
- **Dynamic Media Overlay:** Real-time integration with Windows Media Transport Controls to burn current song titles and album art directly onto frames.
- **Multi-Threaded Architecture:** Decoupled camera and media-fetching logic to ensure zero-latency recording even if system services lag.
- **Auto-Compilation:** One-touch conversion from raw JPEG sequence to `.mp4` video format using OpenCV's VideoWriter.
- **Smart Storage:** Automatic local cleanup and `.gitignore` configurations to prevent repository bloat.
              
## 🛠️ Technical Stack
- **Language:** Python 3.10+
- **Computer Vision:** OpenCV (`cv2`)
- **System Integration:** Windows SDK (`winsdk`) for media session telemetry.
- **Concurrency:** `threading` and `asyncio` for non-blocking hardware I/O.

## 🚀 Quick Start

### Prerequisites
- Windows 10/11
- Python installed and added to PATH

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/James-Xiao26/timelapse-study-tool.git](https://github.com/James-Xiao26/timelapse-study-tool.git)
   cd timelapse-study-tool
