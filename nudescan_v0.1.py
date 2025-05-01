from nudenet import NudeDetector
import os

detector = NudeDetector()

def is_nsfw(image_path):
    if not os.path.exists(image_path):
        print("❌ File not found:", image_path)
        return False

    detections = detector.detect(image_path)
    print("📸 Detection result:", detections)  # 👈

    for d in detections:
        print("🧠 Detection item:", d)  # 👈
        if d.get('class') == 'EXPOSED':
            return True

    return False

