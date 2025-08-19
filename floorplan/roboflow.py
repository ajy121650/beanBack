from inference_sdk import InferenceHTTPClient
import json, cv2

client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="WMgJWPbuVlyxzmjDsndL"
)

result = client.run_workflow(
    workspace_name="cho-voxnn",
    workflow_id="detect-count-and-visualize",
    images={"image": "example.png"},
    use_cache=False
)

print(json.dumps(result, indent=2))

# extract your detections as before…
first      = result[0]
detections = first["predictions"]["predictions"]
img        = cv2.imread("example.png")

for det in detections:
    cx, cy = det["x"], det["y"]
    w, h   = det["width"], det["height"]
    x1, y1 = int(cx-w/2), int(cy-h/2)
    x2, y2 = int(cx+w/2), int(cy+h/2)
    color  = (0,255,0) if "table" in det["class"] else (255,0,0)
    cv2.rectangle(img,(x1,y1),(x2,y2),color,2)
    cv2.putText(img,f"{det['class']}:{det['confidence']:.2f}",
                (x1, max(15,y1-5)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color,2)

cv2.imwrite("rf_overlay.png", img)
print("Saved rf_overlay.png")
