import os
import logging
from moviepy.video.io.VideoFileClip import VideoFileClip
# In MoviePy v2.x, concatenate_videoclips moved to CompositeVideoClip submodule
try:
    from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
except ImportError:
    # Fallback for other MoviePy versions
    try:
        from moviepy.video.compositing.concatenate import concatenate_videoclips
    except ImportError:
        from moviepy.editor import concatenate_videoclips

logger = logging.getLogger(__name__)

class VideoMerger:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def merge_videos(self, video_paths, output_filename):
        """
        Concatenates multiple video files into one.
        """
        # Filter non-existent files
        valid_paths = [p for p in video_paths if os.path.exists(p)]
        
        if not valid_paths:
            logger.warning("No valid videos to merge.")
            return False

        try:
            logger.info(f"Merging {len(valid_paths)} videos into {output_filename}")
            
            clips = []
            for path in valid_paths:
                try:
                    clip = VideoFileClip(path)
                    clips.append(clip)
                except Exception as e:
                    logger.error(f"Failed to load clip {path}: {e}")
            
            if not clips:
                logger.error("No clips were successfully loaded.")
                return False

            # Concatenate clips
            # method="compose" is safer if videos have different resolutions, 
            # but if they are all from the same bot, "chain" (default) is faster.
            # Using compose style logic if needed, but defaults to basic concat first.
            final_clip = concatenate_videoclips(clips, method="compose")
            
            final_output_path = os.path.join(self.output_dir, output_filename)
            
            # Using standard write settings consistent with generator
            final_clip.write_videofile(
                final_output_path,
                fps=24, # Standard for merge or inherited
                codec="libx264",
                audio_codec="aac",
                threads=4,
                logger=None
            )
            
            # Close all clips to free resources
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f"Successfully merged video saved to: {final_output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge videos: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
