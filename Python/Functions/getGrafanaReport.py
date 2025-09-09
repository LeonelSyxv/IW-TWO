import cv2, json, os
from datetime import datetime
from PIL import ImageGrab, Image
import numpy as np

def count_colored_boxes(image: Image.Image):
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

    yellow_lower = np.array([22, 200, 150])
    yellow_upper = np.array([30, 255, 255])

    red_lower1 = np.array([0, 180, 120])
    red_upper1 = np.array([5, 255, 200])
    red_lower2 = np.array([170, 180, 120])
    red_upper2 = np.array([180, 255, 200])

    blue_lower = np.array([105, 70, 200])
    blue_upper = np.array([115, 120, 255])

    mask_yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)
    mask_red = cv2.bitwise_or(
        cv2.inRange(hsv, red_lower1, red_upper1),
        cv2.inRange(hsv, red_lower2, red_upper2)
    )
    mask_blue = cv2.inRange(hsv, blue_lower, blue_upper)

    def count_boxes(mask, min_area=100):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return sum(1 for cnt in contours if cv2.contourArea(cnt) > min_area)

    return {
        "yellow": count_boxes(mask_yellow),
        "red": count_boxes(mask_red),
        "blue": count_boxes(mask_blue)
    }

def get_grafana_report():
    # (Left, Top, Width, Height)
    region = (10, 200, 1585, 860)  
    screenshot = ImageGrab.grab(bbox=region)

    nodejs_images = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../NodeJS/images"))
    os.makedirs(nodejs_images, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(nodejs_images, f"grafana_{timestamp}.png")
    screenshot.save(out_path)

    counts = count_colored_boxes(screenshot)

    total_red = counts.get("red", 0)
    total_yellow = counts.get("yellow", 0)
    total_blue = counts.get("blue", 0)

    if total_red == 0 and total_yellow == 0 and total_blue == 0:
        msg = "✅ Panel OTT de Grafana completamente estable"
    else:
        msg = (
            "📊 Panel OTT de Grafana con:\n\n"
            f"- *{total_red}* Canales fuera.\n"
            f"- *{total_yellow}* Canales alarmados.\n"
            f"- *{total_blue}* Canales en mantenimiento."
        )

    result = {
        "image": out_path,
        "message": msg
    }
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    get_grafana_report()
