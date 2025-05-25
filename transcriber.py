from faster_whisper import WhisperModel
import ffmpeg
import sys

# 使用 ffmpeg 取得音訊長度
def get_audio_duration(audio_path):
    probe = ffmpeg.probe(audio_path)
    return float(probe["format"]["duration"])

# 時間格式化函數
def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def transcribe(audio_path: str, output_path: str = "split_output.srt"):
    # 載入模型與音訊
    model = WhisperModel("large-v2", device="cuda", compute_type="float32")
    duration = get_audio_duration(audio_path)

    # 設定要切出的贅字
    filler_words = ["然後", "就是", "那個"]

    segments, info = model.transcribe(audio_path, language="zh")

    with open(output_path, "w", encoding="utf-8") as f:
        index = 1
        for segment in segments:
            seg_text = segment.text.strip()
            seg_start = segment.start
            seg_end = segment.end

            # 顯示進度
            progress = min(seg_start / duration, 1.0)
            print(f"\r轉換中：{progress*100:.1f}%", end="")

            total_chars = len(seg_text.replace(" ", ""))
            has_filler = False

            for word in filler_words:
                if word in seg_text:
                    parts = seg_text.split(word, 1)
                    pre = parts[0].strip()
                    post = parts[1].strip() if len(parts) > 1 else ""

                    avg_char_duration = (seg_end - seg_start) / total_chars if total_chars else 0.2
                    filler_start = seg_start + len(pre) * avg_char_duration
                    filler_end = filler_start + len(word) * avg_char_duration

                    # 輸出贅字成一段
                    f.write(f"{index}\n")
                    f.write(f"{format_timestamp(filler_start)} --> {format_timestamp(filler_end)}\n")
                    f.write(f"{word}\n\n")
                    index += 1

                    # 輸出剩下的句子（不包含贅字）
                    if post:
                        rest_start = filler_end
                        rest_end = seg_end
                        f.write(f"{index}\n")
                        f.write(f"{format_timestamp(rest_start)} --> {format_timestamp(rest_end)}\n")
                        f.write(f"{post}\n\n")
                        index += 1

                    has_filler = True
                    break  # 只處理一個贅字 per segment

            if not has_filler:
                f.write(f"{index}\n")
                f.write(f"{format_timestamp(seg_start)} --> {format_timestamp(seg_end)}\n")
                f.write(f"{seg_text}\n\n")
                index += 1

    print("\n✅ 處理完成！輸出為", output_path)
    return output_path

