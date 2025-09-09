# Wrist Motion Capture System

A computer vision-based system for tracking and analyzing wrist range of motion (ROM) using colored markers. Designed for physical therapy and rehabilitation tracking with real-time feedback and comprehensive progress analytics.

## Demo

[Watch Software Walkthrough](Software%20Walkthrough.mp4)
*Complete demonstration of the wrist motion capture system in action*

## Features

### 🎯 Real-Time Motion Tracking
- **Color Marker Detection**: Tracks orange, yellow, pink, and blue markers
- **Angle Calculation**: Precise measurement of radial and ulnar deviation angles
- **Live Feedback**: Instant "GREAT", "TOO FAR", or "TOO LITTLE" guidance
- **Dual Arm Support**: Configurable for left or right wrist

### 📊 Progress Analytics
- **Session Tracking**: Duration, movement count, and accuracy percentage
- **Personal Bests**: Maximum achieved angles for both movement types
- **Trend Analysis**: Shows improvement, decline, or stable performance patterns
- **Historical Data**: Session summaries saved for long-term progress tracking

### 🎮 Interactive Controls
- **Manual Recording**: Press `SPACEBAR` to capture specific angles
- **Reset Function**: Press `R` to clear recorded measurements
- **Easy Exit**: Press `ESC` to save session and exit

### 💾 Data Storage
- **results.csv**: Continuous logging of all movements with timestamps
- **recorded_angles.csv**: Manually recorded angle measurements
- **progress_history.json**: Comprehensive session analytics and trends

## Installation

### Prerequisites
- Python 3.7 or higher
- Webcam/camera for motion capture
- Colored markers (orange, yellow, pink, blue)

### Install Dependencies
```bash
pip install numpy opencv-python pysine statistics
```

### Quick Start
```bash
git clone https://github.com/yourusername/wrist-motion-capture.git
cd wrist-motion-capture
python mocap.py
```

## Usage

### Setup
1. **Attach Markers**: Secure colored markers to your wrist device
2. **Position Camera**: Ensure clear view of all markers
3. **Configure Lighting**: Good lighting improves marker detection

### Initial Configuration
When you run the program, you'll be prompted to enter:
- **Arm Selection**: Left (L) or Right (R) wrist
- **ROM Targets**: Minimum and maximum angles for radial deviation
- **ROM Targets**: Minimum and maximum angles for ulnar deviation

### During Session
- **Live Display**: Three windows show camera feed, marker tracking, and progress
- **Real-time Feedback**: Visual and text feedback on movement quality
- **Manual Recording**: Press `SPACEBAR` when you achieve a target angle
- **Reset Recordings**: Press `R` to clear manual recordings
- **Exit**: Press `ESC` to save session and close

### Controls Reference
| Key | Action |
|-----|--------|
| `ESC` | Exit and save session |
| `SPACEBAR` | Record current angle |
| `R` | Reset recorded angles |

## Understanding the Display

### Main Windows
1. **Camera Feed**: Raw camera input
2. **Angle Tracking**: Processed view with marker detection and lines
3. **Progress Display**: Statistics and feedback overlay

### Progress Information
- **Current Angle**: Live angle measurement with movement type
- **Session Stats**: Total movements and accuracy percentage
- **Personal Bests**: Maximum achieved angles
- **Recorded Angles**: Count and last manually recorded value
- **Trend Indicator**: Performance trajectory (↗ ↘ →)

## Data Analysis

### Session Summary
At the end of each session, you'll see:
```
=== SESSION SUMMARY ===
Duration: 5.2 minutes
Total movements: 150
Accuracy: 78.5%
Average angle: 42.3°
Radial movements: 75 (max: 65.2°)
Ulnar movements: 75 (max: 58.7°)
Manual recordings: 8 angles saved
Recorded angles: [45.2, 52.1, 38.9, 61.3, 44.7, 59.8, 47.2, 55.6]
=======================
```

### Data Files
- **results.csv**: Timestamp, angle, movement type, feedback for every movement
- **recorded_angles.csv**: Manually recorded measurements with context
- **progress_history.json**: Session analytics for tracking improvement over time

## Adding Demo Media

To include your demo photo/video:

### For Screenshots
1. Create a `demo` folder in your project directory
2. Add your screenshot as `demo/screenshot.png`
3. The README will automatically reference it

### For Videos
1. Add your video file as `demo/demo_video.mp4`
2. Alternative: Upload to YouTube/Vimeo and replace the link:
   ```markdown
   [Watch Demo Video](https://youtu.be/your-video-id)
   ```

### File Structure
```
wrist-motion-capture/
├── mocap.py                 # Main application
├── README.md               # This file
├── demo/                   # Demo media folder
│   ├── screenshot.png      # Interface screenshot
│   └── demo_video.mp4      # Sample session video
├── results.csv             # Generated: Movement data
├── recorded_angles.csv     # Generated: Manual recordings
└── progress_history.json   # Generated: Session summaries
```

## Troubleshooting

### Common Issues
- **Camera not detected**: Ensure webcam is connected and not used by other apps
- **Markers not tracking**: Check lighting and color contrast
- **ESC not working**: Click on camera window first, then press ESC
- **Import errors**: Run `pip install` command for missing packages

### Marker Detection Tips
- Use bright, distinct colors (orange, yellow, pink, blue)
- Ensure good lighting without shadows
- Keep markers visible to camera at all times
- Clean marker surfaces for better color detection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with OpenCV for computer vision capabilities
- Designed for physical therapy and rehabilitation applications
- Supports research in motion analysis and recovery tracking

---

**Note**: This system is for educational and research purposes. Consult healthcare professionals for medical applications.