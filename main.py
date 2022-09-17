from location_data_detection import get_location_data
from crop_event import crop_event
from eye_gestures_detection import detect_eye_gestures
from play_translation_audio import play_translation_audio
from screenshot_event import screenshot_event
from translation_event import translation_event

PLACEHOLDER = None

location_data = []

#CALIBRATE
def main():
    while (True):
        location_data.append(get_location_data(PLACEHOLDER))
        eye_gestures = detect_eye_gestures(PLACEHOLDER)
        if (eye_gestures == "blink"):
            break

if __name__ == "__main__":
    main()