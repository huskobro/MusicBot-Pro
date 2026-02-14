import os
import random
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, VideoClip
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_video(self, audio_path, image_path, output_filename, effect_type="None"):
        """
        Generates an MP4 video by combining audio and image with optional effects.
        effect_type: "None", "Snow", "Rain", "Particles"
        """
        try:
            logger.info(f"Generating video for {audio_path} with effect {effect_type}")
            
            # 1. Load Audio
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return False
            
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # 2. Load Image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False
                
            base_clip = ImageClip(image_path).set_duration(duration)
            
            # 3. Apply Effects
            final_clip = base_clip
            if effect_type and effect_type != "None":
                effect_clip = self._create_procedural_effect(effect_type, duration, base_clip.size)
                if effect_clip:
                    final_clip = CompositeVideoClip([base_clip, effect_clip])
            
            # 4. Set Audio and Write
            final_clip = final_clip.set_audio(audio)
            
            output_path = os.path.join(self.output_dir, output_filename)
            final_clip.write_videofile(
                output_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                threads=4,
                logger=None # Suppress moviepy stdout spam
            )
            
            logger.info(f"Video generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _create_procedural_effect(self, effect_type, duration, resolution):
        """Generates a procedural effect clip using numpy and moviepy."""
        w, h = resolution
        
        if effect_type == "Snow":
            # Snow: White particles moving down
            num_particles = 100
            # State: x, y, speed, size
            particles = np.zeros((num_particles, 4))
            particles[:, 0] = np.random.randint(0, w, num_particles) # x
            particles[:, 1] = np.random.randint(0, h, num_particles) # y
            particles[:, 2] = np.random.uniform(2, 5, num_particles) # speed
            particles[:, 3] = np.random.uniform(1, 3, num_particles) # size

            def make_frame(t):
                # Update positions
                particles[:, 1] += particles[:, 2] # y += speed
                # Reset if out of bounds
                mask = particles[:, 1] > h
                particles[mask, 1] = 0
                particles[mask, 0] = np.random.randint(0, w, np.sum(mask))

                # Draw
                frame = np.zeros((h, w, 4), dtype=np.uint8) # RGBA
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    # Draw a simple white square/circle approximation
                    # Simple efficient drawing without cv2 dependency if possible
                    # Or just direct array manipulation
                    r_start = max(0, y)
                    r_end = min(h, y+s)
                    c_start = max(0, x)
                    c_end = min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = [255, 255, 255, 200]
                return frame

            return VideoClip(make_frame, duration=duration, ismask=False).set_position("center")

        elif effect_type == "Rain":
            # Rain: Thin lines moving fast down
            # Using slightly blue-ish tint
             # Rain: Blue/White lines moving fast down
            num_particles = 200
            particles = np.zeros((num_particles, 4))
            particles[:, 0] = np.random.randint(0, w, num_particles)
            particles[:, 1] = np.random.randint(0, h, num_particles)
            particles[:, 2] = np.random.uniform(15, 25, num_particles) # fast speed
            particles[:, 3] = np.random.uniform(1, 2, num_particles) # thickness

            def make_frame(t):
                particles[:, 1] += particles[:, 2]
                mask = particles[:, 1] > h
                particles[mask, 1] = 0
                particles[mask, 0] = np.random.randint(0, w, np.sum(mask))

                frame = np.zeros((h, w, 4), dtype=np.uint8)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    length = int(s * 5)
                    r_start = max(0, y)
                    r_end = min(h, y+length)
                    c_start = max(0, x)
                    c_end = min(w, x+s)
                    # Light blue rain
                    frame[r_start:r_end, c_start:c_end] = [200, 200, 255, 150]
                return frame
            
            return VideoClip(make_frame, duration=duration, ismask=False).set_position("center")
            
        elif effect_type == "Particles":
             # Particles: Floating up slowly, golden
            num_particles = 80
            particles = np.zeros((num_particles, 5)) # x, y, speed, size, wobble_offset
            particles[:, 0] = np.random.randint(0, w, num_particles)
            particles[:, 1] = np.random.randint(0, h, num_particles)
            particles[:, 2] = np.random.uniform(0.5, 1.5, num_particles) # slow up speed
            particles[:, 3] = np.random.uniform(2, 4, num_particles) # size
            particles[:, 4] = np.random.uniform(0, 2*np.pi, num_particles)

            def make_frame(t):
                particles[:, 1] -= particles[:, 2] # y -= speed (up)
                particles[:, 0] += np.sin(t + particles[:, 4]) * 0.5 # wobble x
                
                mask = particles[:, 1] < 0
                particles[mask, 1] = h
                particles[mask, 0] = np.random.randint(0, w, np.sum(mask))

                frame = np.zeros((h, w, 4), dtype=np.uint8)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    r_start = max(0, y)
                    r_end = min(h, y+s)
                    c_start = max(0, x)
                    c_end = min(w, x+s)
                    # Gold/Yellow
                    frame[r_start:r_end, c_start:c_end] = [255, 215, 0, 180]
                return frame
            
            return VideoClip(make_frame, duration=duration, ismask=False).set_position("center")

        return None

if __name__ == "__main__":
    # Test block
    print("Testing Video Generator...")
    # Mock files would be needed here
