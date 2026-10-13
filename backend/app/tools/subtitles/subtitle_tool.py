import os
from typing import List, Dict, Any
from ...utils.logger import logger

class SubtitleTool:
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @classmethod
    def generate_srt(
        cls,
        scenes: List[Dict[str, Any]],
        output_path: str,
        srt_text_override: str = ""
    ) -> str:
        """
        Generate synchronized SRT file from scene narration or word timestamps.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if srt_text_override and srt_text_override.strip():
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(srt_text_override.strip() + "\n")
            return output_path

        srt_entries = []
        entry_idx = 1
        current_time = 0.5  # slight delay for opening hook

        for scene in scenes:
            narration = scene.get("narration", "").strip()
            scene_duration = float(scene.get("duration", 5.0))
            
            if not narration:
                current_time += scene_duration
                continue

            # Split narration into punchy chunks (3 to 6 words each for social media)
            words = narration.split()
            chunk_size = 5
            chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            
            chunk_duration = (scene_duration - 0.4) / max(1, len(chunks))

            for chunk in chunks:
                start_sec = current_time
                end_sec = current_time + chunk_duration
                
                srt_entries.append(
                    f"{entry_idx}\n"
                    f"{cls.format_timestamp(start_sec)} --> {cls.format_timestamp(end_sec)}\n"
                    f"{chunk}\n"
                )
                entry_idx += 1
                current_time = end_sec

            # Advance to end of scene if any time remains
            current_time = max(current_time, current_time + 0.2)

        srt_content = "\n".join(srt_entries)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        logger.info(f"[SubtitleTool] Created subtitle file ({len(srt_entries)} cues) -> {output_path}")
        return output_path
