from nudenet import NudeDetector

# Initialize the detector
detector = NudeDetector()

# Replace with your image path
image_path = "nudity.png"

# Detect content
detections = detector.detect(image_path)
print("Detections:", detections)

# Define category logic
EXPLICIT_CLASSES = {
    'FEMALE_BREAST_EXPOSED',
    'FEMALE_GENITALIA_EXPOSED',
    'MALE_GENITALIA_EXPOSED',
    'BUTTOCKS_EXPOSED',
    'ANUS_EXPOSED'
}

BORDERLINE_CLASSES = {
    'FEMALE_BREAST_COVERED',
    'FEMALE_GENITALIA_COVERED',
    'BELLY_EXPOSED',
    'ARMPITS_EXPOSED'
}

def categorize_image(detections):
    for item in detections:
        if item['class'] in EXPLICIT_CLASSES and item['score'] >= 0.75:
            return 'explicit'
        elif item['class'] in BORDERLINE_CLASSES and item['score'] >= 0.6:
            return 'borderline'
    return 'safe'

# Print the category
category = categorize_image(detections)
print(f"Category: {category.upper()}")
