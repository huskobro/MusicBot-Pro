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

    def merge_videos(self, video_paths, base_output_filename, target_duration_mins=0, fade_out_enabled=False):
        """
        Concatenates multiple video files into one or more files based on target duration.
        """
        # Filter non-existent files
        valid_paths = [p for p in video_paths if os.path.exists(p)]
        
        if not valid_paths:
            logger.warning("No valid videos to merge.")
            return False

        try:
            logger.info(f"Merging {len(valid_paths)} videos. Target duration: {target_duration_mins} mins.")
            
            target_duration_secs = target_duration_mins * 60
            
            current_part = 1
            current_clips = []
            current_duration = 0.0
            current_timestamps = []  # List of (timestamp_str, name)
            
            def write_chunk(clips_to_write, timestamps_to_write, part_num, is_single_part=False):
                if not clips_to_write: return
                
                # Format filename
                name_no_ext, ext = os.path.splitext(base_output_filename)
                if is_single_part:
                    out_name = f"{name_no_ext}{ext}"
                else:
                    out_name = f"{name_no_ext}_part{part_num}{ext}"
                
                out_path = os.path.join(self.output_dir, out_name)
                txt_path = os.path.join(self.output_dir, f"{os.path.splitext(out_name)[0]}.txt")
                
                # Write timestamps to txt
                try:
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        for ts, name in timestamps_to_write:
                            f.write(f"{ts} {name}\n")
                    logger.info(f"Timestamps saved to: {txt_path}")
                except Exception as e:
                    logger.error(f"Failed to write timestamps to {txt_path}: {e}")
                
                # Write video
                logger.info(f"Writing compiled video chunk: {out_name} ({len(clips_to_write)} target clips)")
                final_clip = concatenate_videoclips(clips_to_write, method="compose")
                final_clip.write_videofile(
                    out_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    threads=4,
                    logger=None
                )
                final_clip.close()
                logger.info(f"Successfully merged video saved to: {out_path}")
                
                # Close individual clips to free resources
                for c in clips_to_write:
                    c.close()

            import re
            def format_timestamp(seconds):
                m, s = divmod(int(seconds), 60)
                h, m = divmod(m, 60)
                if h > 0:
                    return f"{h:02d}:{m:02d}:{s:02d}"
                return f"{m:02d}:{s:02d}"

            def extract_name(filename):
                # E.g., 1_Échos_de_la_Pluie_1.mp4 -> Échos de la Pluie
                base = os.path.splitext(os.path.basename(filename))[0]
                pattern = re.compile(r'^\d+_+(.+?)_+\d+$', re.IGNORECASE)
                match = pattern.match(base)
                if match:
                    return match.group(1).replace('_', ' ')
                return base.replace('_', ' ')

            for i, path in enumerate(valid_paths):
                try:
                    clip = VideoFileClip(path)
                    
                    if fade_out_enabled:
                        # Apply 2 second fade out to audio
                        try:
                            if clip.audio:
                                clip = clip.with_audio(clip.audio.audio_fadeout(2))
                        except Exception as fade_err:
                            logger.error(f"Failed to apply fade out to {path}: {fade_err}")
                            
                    clip_len = clip.duration
                    
                    # If adding this clip exceeds target duration (and it's not the very first clip in the chunk)
                    if target_duration_secs > 0 and current_clips and (current_duration + clip_len > target_duration_secs):
                        # Write what we have so far
                        write_chunk(current_clips, current_timestamps, current_part, is_single_part=False)
                        current_part += 1
                        current_clips = []
                        current_duration = 0.0
                        current_timestamps = []
                    
                    # Add clip to current chunk
                    # Timestamp is the start of this clip relative to the current chunk
                    ts_str = format_timestamp(current_duration)
                    song_name = extract_name(path)
                    
                    current_timestamps.append((ts_str, song_name))
                    current_clips.append(clip)
                    current_duration += clip_len
                    
                except Exception as e:
                    logger.error(f"Failed to load clip {path}: {e}")
            
            # Write remaining clips
            if current_clips:
                is_single = (current_part == 1)
                write_chunk(current_clips, current_timestamps, current_part, is_single_part=is_single)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge videos: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
