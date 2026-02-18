import os
import re
import random
import numpy as np
from moviepy.video.VideoClip import VideoClip, ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_video(self, audio_path, image_path, output_filename, effect_types=None, fps=24, resolution="Vertical (Shorts - 1080x1920)", intensity=50, progress_callback=None, threads=1):
        """
        Generates an MP4 video by combining audio and image with optional multiple effects.
        """
        if effect_types is None:
            effect_types = ["None"]

        try:
            # Custom Logger for MoviePy 2.x (Compatible with proglog)
            class MoviePyProgressLogger:
                def __init__(self, callback, rid):
                    self.callback = callback
                    self.rid = rid
                    self.state = {}
                def __call__(self, **kwargs): pass
                def callback(self, **kwargs): pass
                def message(self, *args, **kwargs): pass
                def bars_callback(self, bar, attr, value, total):
                    if self.callback and total > 0:
                        percent = min(100, int((value / total) * 100))
                        self.callback(self.rid, f"Rendering Video... {percent}% 🎬")
                def iter_bar(self, **kwargs):
                    # Return the iterable for the loop to function
                    for name, iterable in kwargs.items():
                        if name == 'bar': continue
                        return iterable
                    return []
                def update_bar(self, bar, index): pass

            # Extract rid from filename if possible
            rid = output_filename.split("_")[0] if "_" in output_filename else "video"
            rid = re.sub(r'[^\w\-_]', '', rid) # Clean special chars for temp files

            logger.info(f"Generating video for {audio_path} with effects {effect_types}. Output: {output_filename}")
            
            # Resolve Resolution
            res_map = {
                "Vertical (Shorts - 1080x1920)": (1080, 1920),
                "Dikey (Shorts - 1080x1920)": (1080, 1920),
                "Horizontal (HD - 1920x1080)": (1920, 1080),
                "Yatay (HD - 1920x1080)": (1920, 1080),
                "Horizontal (SD - 1280x720)": (1280, 720),
                "Yatay (SD - 1280x720)": (1280, 720)
            }
            target_res = res_map.get(resolution, (1080, 1920))
            
            # 1. Load Audio
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                return False
            
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            if not duration or duration <= 0:
                logger.error("Audio duration is 0 or invalid.")
                return False
            
            # 2. Load Image and Resize/Crop to fill resolution
            img_clip = ImageClip(image_path)
            w_ratio = target_res[0] / img_clip.w
            h_ratio = target_res[1] / img_clip.h
            scale = max(w_ratio, h_ratio)
            
            base_clip = img_clip.resized(scale)
            base_clip = base_clip.cropped(
                x_center=base_clip.w/2, 
                y_center=base_clip.h/2, 
                width=target_res[0], 
                height=target_res[1]
            ).with_duration(duration)
            
            logger.info(f"Base clip size: {base_clip.size}")
            
            # 3. Apply Effects
            current_clip = base_clip
            
            # Custom Ken Burns Effect (Zoom)
            if any(eff in effect_types for eff in ["Ken Burns (Zoom)", "Yakınlaşma (Ken Burns)"]):
                zoom_speed = 0.05 * (intensity / 50)
                current_clip = base_clip.resized(lambda t: 1 + zoom_speed * t)
            
            # Collect procedural overlay effects
            overlay_clips = []
            for effect_type in effect_types:
                if effect_type and effect_type != "None" and "Ken Burns" not in effect_type and "Yakınlaşma" not in effect_type:
                    effect_clip = self._create_procedural_effect(effect_type, duration, target_res, intensity)
                    if effect_clip:
                        overlay_clips.append(effect_clip)
            
            if overlay_clips:
                final_clip = CompositeVideoClip([current_clip] + overlay_clips, size=target_res)
            else:
                final_clip = current_clip
            
            logger.info(f"Final clip resolution: {final_clip.size}")
            
            # 4. Set Audio and Write
            final_clip = final_clip.with_audio(audio)
            
            output_path = os.path.join(self.output_dir, output_filename)
            temp_audio_path = os.path.join(self.output_dir, f"temp_{rid}.m4a")
            
            logger.info(f"Targeting: {output_path}")
            
            # Final Write
            final_clip.write_videofile(
                output_path, 
                fps=fps, 
                codec="libx264", 
                audio_codec="aac",
                temp_audiofile=temp_audio_path,
                threads=threads,
                logger=MoviePyProgressLogger(progress_callback, rid) if progress_callback else None
            )
            
            # Cleanup temp audio
            if os.path.exists(temp_audio_path):
                try: os.remove(temp_audio_path)
                except: pass
                
            if os.path.exists(output_path):
                logger.info(f"Video generated successfully: {output_path}")
                return True
            else:
                logger.error(f"Video file NOT found after render: {output_path}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _create_procedural_effect(self, effect_type, duration, resolution, intensity=50):
        """Generates a procedural effect clip using numpy and moviepy."""
        w, h = resolution
        
        if effect_type in ["Snow", "Kar Efekti"]:
            num_particles = int(2 * intensity)
            particles = np.zeros((num_particles, 4))
            particles[:, 0] = np.random.randint(0, w, num_particles)
            particles[:, 1] = np.random.randint(0, h, num_particles)
            particles[:, 2] = np.random.uniform(1, 4, num_particles) * (intensity / 50) # speed
            particles[:, 3] = np.random.uniform(1, 4, num_particles) # size

            def make_frame(t):
                particles[:, 1] += particles[:, 2]
                mask_f = particles[:, 1] > h
                particles[mask_f, 1] = 0
                particles[mask_f, 0] = np.random.randint(0, w, np.sum(mask_f))
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    r_start, r_end = max(0, y), min(h, y+s)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = [255, 255, 255]
                return frame
                
            def make_mask(t):
                frame = np.zeros((h, w), dtype=float)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    r_start, r_end = max(0, y), min(h, y+s)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = 0.7 # Alpha
                return frame

            clip = VideoClip(make_frame, duration=duration).with_position("center")
            clip.mask = VideoClip(make_mask, is_mask=True, duration=duration)
            return clip

        elif effect_type in ["Rain", "Yağmur Efekti"]:
            num_particles = int(4 * intensity)
            particles = np.zeros((num_particles, 4))
            particles[:, 0] = np.random.randint(0, w, num_particles)
            particles[:, 1] = np.random.randint(0, h, num_particles)
            particles[:, 2] = np.random.uniform(10, 30, num_particles) * (intensity / 50)
            particles[:, 3] = np.random.uniform(1, 3, num_particles)

            def make_frame(t):
                particles[:, 1] += particles[:, 2]
                mask_f = particles[:, 1] > h
                particles[mask_f, 1] = 0
                particles[mask_f, 0] = np.random.randint(0, w, np.sum(mask_f))
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    length = int(s * 8)
                    r_start, r_end = max(0, y), min(h, y+length)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = [180, 200, 255]
                return frame

            def make_mask(t):
                frame = np.zeros((h, w), dtype=float)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    length = int(s * 8)
                    r_start, r_end = max(0, y), min(h, y+length)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = 0.5
                return frame

            clip = VideoClip(make_frame, duration=duration).with_position("center")
            clip.mask = VideoClip(make_mask, is_mask=True, duration=duration)
            return clip
            
        elif effect_type in ["Particles", "Parçacıklar"]:
            num_particles = int(1.5 * intensity)
            particles = np.zeros((num_particles, 5))
            particles[:, 0] = np.random.randint(0, w, num_particles)
            particles[:, 1] = np.random.randint(0, h, num_particles)
            particles[:, 2] = np.random.uniform(0.5, 2, num_particles) * (intensity / 50)
            particles[:, 3] = np.random.uniform(2, 6, num_particles)
            particles[:, 4] = np.random.uniform(0, 2*np.pi, num_particles)

            def make_frame(t):
                particles[:, 1] -= particles[:, 2]
                particles[:, 0] += np.sin(t + particles[:, 4]) * 0.8
                mask_f = particles[:, 1] < 0
                particles[mask_f, 1] = h
                particles[mask_f, 0] = np.random.randint(0, w, np.sum(mask_f))
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    r_start, r_end = max(0, y), min(h, y+s)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = [255, 220, 100]
                return frame
                
            def make_mask(t):
                frame = np.zeros((h, w), dtype=float)
                for p in particles:
                    x, y, s = int(p[0]), int(p[1]), int(p[3])
                    r_start, r_end = max(0, y), min(h, y+s)
                    c_start, c_end = max(0, x), min(w, x+s)
                    frame[r_start:r_end, c_start:c_end] = 0.6
                return frame

            clip = VideoClip(make_frame, duration=duration).with_position("center")
            clip.mask = VideoClip(make_mask, is_mask=True, duration=duration)
            return clip

        elif effect_type == "Glitch" or effect_type == "Bozulma (Glitch)":
            def make_frame(t):
                frame = np.zeros((h, w, 3), dtype=np.uint8)
                if random.random() < (0.1 * intensity / 50):
                    y_slice = random.randint(0, h-50)
                    h_slice = random.randint(20, 100)
                    r_start, r_end = max(0, y_slice), min(h, y_slice+h_slice)
                    frame[r_start:r_end, :, 0] = 255 # Red shift
                return frame
                
            def make_mask(t):
                frame = np.zeros((h, w), dtype=float)
                if random.random() < (0.1 * intensity / 50):
                    y_slice = random.randint(0, h-50)
                    h_slice = random.randint(20, 100)
                    r_start, r_end = max(0, y_slice), min(h, y_slice+h_slice)
                    frame[r_start:r_end, :] = 0.2
                return frame

            clip = VideoClip(make_frame, duration=duration).with_position("center")
            clip.mask = VideoClip(make_mask, is_mask=True, duration=duration)
            return clip

        elif effect_type == "Vignette" or effect_type == "Köşe Karartma (Vignette)":
            def make_frame(t):
                return np.zeros((h, w, 3), dtype=np.uint8) # Full black, mask handles shading

            def make_mask(t):
                Y, X = np.ogrid[:h, :w]
                center_y, center_x = h / 2, w / 2
                dist_from_center = np.sqrt((X - center_x)**2 + (Y - center_y)**2)
                max_dist = np.sqrt(center_x**2 + center_y**2)
                radius = 1.0 - (intensity / 150)
                vignette = 1.0 - np.clip((dist_from_center / (max_dist * radius)), 0, 1)
                return (1.0 - vignette) * 0.8 # Variable alpha mask

            clip = VideoClip(make_frame, duration=duration).with_position("center")
            clip.mask = VideoClip(make_mask, is_mask=True, duration=duration)
            return clip

        return None

if __name__ == "__main__":
    # Test block
    print("Testing Video Generator...")
    # Mock files would be needed here
