import os
import subprocess
from typing import List, Optional, Tuple
from ...utils.logger import logger

class FFmpegEditorTool:
    """
    FFmpeg video editing and rendering engine.
    Handles stitching video clips, audio layering & ducking, subtitle burning,
    aspect ratio enforcement, and web-ready MP4 exports.
    """

    @staticmethod
    def get_media_info(file_path: str) -> dict:
        """Probe media file for duration, dimensions, and streams."""
        if not os.path.exists(file_path):
            return {"exists": False}
        
        cmd = f'ffprobe -v error -show_entries format=duration,size:stream=codec_name,codec_type,width,height -of json "{file_path}"'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            import json
            try:
                data = json.loads(res.stdout)
                duration = float(data.get("format", {}).get("duration", 0))
                size = int(data.get("format", {}).get("size", 0))
                streams = data.get("streams", [])
                has_video = any(s.get("codec_type") == "video" for s in streams)
                has_audio = any(s.get("codec_type") == "audio" for s in streams)
                v_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
                width = v_stream.get("width", 0)
                height = v_stream.get("height", 0)
                return {
                    "exists": True,
                    "duration": duration,
                    "size_bytes": size,
                    "has_video": has_video,
                    "has_audio": has_audio,
                    "width": width,
                    "height": height
                }
            except Exception:
                pass
        return {"exists": True, "duration": 0, "has_video": True, "has_audio": False}

    @classmethod
    def concatenate_scenes(
        cls,
        scene_paths: List[str],
        output_path: str,
        aspect_ratio: str = "9:16"
    ) -> str:
        """Concatenate multiple scene videos into a unified visual track."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write concat list file
        concat_list_file = output_path.replace(".mp4", "_concat_list.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for path in scene_paths:
                clean_path = path.replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        # Concat using demuxer
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_list_file}" -c:v libx264 -pix_fmt yuv420p -preset fast "{output_path}"'
        logger.info(f"[FFmpegEditor] Concatenating {len(scene_paths)} scene clips...")
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if os.path.exists(concat_list_file):
            try:
                os.remove(concat_list_file)
            except Exception:
                pass

        if res.returncode != 0 and not os.path.exists(output_path):
            raise RuntimeError(f"FFmpeg scene concatenation failed: {res.stderr[:200]}")

        return output_path

    @classmethod
    def build_final_video(
        cls,
        scene_paths: List[str],
        voice_path: Optional[str],
        music_path: Optional[str],
        subtitle_path: Optional[str],
        output_path: str,
        aspect_ratio: str = "9:16",
        captions_enabled: bool = True
    ) -> str:
        """
        Assemble final production MP4 with video scenes, voiceover, ducked music, 
        and optional burned subtitles.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        logger.info(f"[FFmpegEditor] Building final video -> {output_path}")

        # Step 1: Concat visuals
        temp_video = output_path.replace(".mp4", "_raw_video.mp4")
        cls.concatenate_scenes(scene_paths, temp_video, aspect_ratio)

        # Get video duration
        v_info = cls.get_media_info(temp_video)
        total_duration = v_info.get("duration", 30.0)

        # Step 2: Mix Audio (Voice + Background Music with Ducking)
        temp_audio = output_path.replace(".mp4", "_mixed_audio.mp3")
        
        has_voice = voice_path and os.path.exists(voice_path)
        has_music = music_path and os.path.exists(music_path)

        if has_voice and has_music:
            # Duck music volume to 18% under voice narration, pad to full video duration
            audio_filter = f"[0:a]volume=1.0[voice];[1:a]volume=0.18,afade=t=in:ss=0:d=1.5,afade=t=out:st={max(1, total_duration - 2)}:d=2[music];[voice][music]amix=inputs=2:duration=longest:dropout_transition=2[aout]"
            cmd = f'ffmpeg -y -i "{voice_path}" -i "{music_path}" -filter_complex "{audio_filter}" -map "[aout]" -t {total_duration} -ac 2 -b:a 192k "{temp_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True)
        elif has_voice:
            # Only voice
            cmd = f'ffmpeg -y -i "{voice_path}" -ac 2 -b:a 192k "{temp_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True)
        elif has_music:
            # Only music
            cmd = f'ffmpeg -y -i "{music_path}" -t {total_duration} -ac 2 -b:a 192k "{temp_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True)
        else:
            # Silent track
            cmd = f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t {total_duration} "{temp_audio}"'
            subprocess.run(cmd, shell=True, capture_output=True)

        # Step 3: Combine Video + Mixed Audio + Subtitles (if enabled and file exists)
        sub_filter = ""
        if captions_enabled and subtitle_path and os.path.exists(subtitle_path):
            # Format subtitle filter for Windows path
            clean_sub_path = subtitle_path.replace("\\", "/").replace(":", "\\:")
            # Use drawtext or subtitles filter with styling
            # Style: yellow text, black border, centered near bottom
            sub_filter = f"-vf \"subtitles='{clean_sub_path}':force_style='FontName=Arial,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,Alignment=2,MarginV=35'\""

        final_cmd = (
            f'ffmpeg -y -i "{temp_video}" -i "{temp_audio}" '
            f'{sub_filter} '
            f'-c:v libx264 -pix_fmt yuv420p -preset fast -crf 20 '
            f'-c:a aac -b:a 192k -shortest "{output_path}"'
        )

        res = subprocess.run(final_cmd, shell=True, capture_output=True, text=True)

        # Cleanup intermediate files
        for temp_f in [temp_video, temp_audio]:
            if os.path.exists(temp_f):
                try:
                    os.remove(temp_f)
                except Exception:
                    pass

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            # Fallback if subtitle filter failed due to fontconfig
            fallback_cmd = (
                f'ffmpeg -y -i "{temp_video}" -i "{temp_audio}" '
                f'-c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "{output_path}"'
            )
            subprocess.run(fallback_cmd, shell=True, capture_output=True)

        # Create master poster / thumbnail
        poster_path = output_path.replace(".mp4", "_poster.jpg").replace("final", "thumbnails")
        os.makedirs(os.path.dirname(poster_path), exist_ok=True)
        os.system(f'ffmpeg -y -ss 00:00:01 -i "{output_path}" -vframes 1 -q:v 2 "{poster_path}" >nul 2>&1')

        logger.info(f"[FFmpegEditor] Final video rendered successfully ({os.path.getsize(output_path)} bytes) -> {output_path}")
        return output_path
