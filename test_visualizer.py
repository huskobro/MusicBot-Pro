import os
from execution.video_generator import VideoGenerator

# Ensure we are in the correct directory
os.chdir('/Users/huseyincoskun/Downloads/Antigravity Proje/MusicBot')

def test_visualizer():
    print("Testing Video Generator with Audio Visualizer...")
    
    # Needs a 5-second audio clip and a dummy image for testing
    audio_path = "test_audio.mp3"
    image_path = "test_image.jpg"
    
    # We will use ffmpeg to create a quick 5-second sine wave and a black image if they don't exist
    if not os.path.exists(audio_path):
        os.system(f"ffmpeg -f lavfi -i sine=frequency=440:duration=5 {audio_path} -y")
    if not os.path.exists(image_path):
        os.system(f"ffmpeg -f lavfi -i color=c=black:s=1080x1920:d=1 -vframes 1 {image_path} -y")

    vgen = VideoGenerator(output_dir="output_test")
    
    success = vgen.generate_video(
        audio_path=audio_path,
        image_path=image_path,
        output_filename="test_visualizer.mp4",
        effect_types=["Audio Visualizer"],
        fps=24,
        resolution="Vertical (Shorts - 1080x1920)",
        intensity=50
    )
    
    if success:
        print("Success! Video generated at output_test/test_visualizer.mp4")
    else:
        print("Failed to generate video.")

if __name__ == "__main__":
    test_visualizer()
