from ultralytics import YOLO
import cv2
import numpy as np

# Load the trained model
model  = YOLO(r"runs/detect/vehicle-detection/baseline_model_gtx1650_12s/weights/best.pt")


# Move model to GPU if available
try:
    model.to("cuda")  # or "cuda" if GPU is available
except Exception as e:
    print(f"Could not move model to GPU: {e}. Using CPU instead.")


# Function for image inference
def image_inference(pil_image, conf_thres: float = 0.1):

    # Convert PIL image to OpenCV format
    img_rgb = np.array(pil_image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    # Inference
    results = model(img_rgb)[0]

    # Vehicle counting
    counts = {"car": 0, "bus": 0, "van": 0}

    # Draw boxes and count vehicles
    for box in results.boxes:
        # Confidence thresholding
        conf = float(box.conf[0])
        if conf < conf_thres:
            continue


        # Extract box coordinates and class
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
        cls_id = int(box.cls[0])
        cls_name = results.names[cls_id]

        # Update count if valid class
        if cls_name in counts:
            counts[cls_name] += 1

        label = f"{cls_name} {conf:.2f}"

        # Draw box & label
        cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img_bgr, (x1, y1 - th - 4), (x1 + tw, y1), (0, 255, 0), -1)
        cv2.putText(img_bgr, label, (x1, y1 - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


    # Draw legend (bottom-left)
    legend_x = 10
    legend_y = img_bgr.shape[0] - 80  # bottom-left region
    line_height = 22

    legend_text = [
        "Vehicle Counts:",
        f"Car: {counts['car']}",
        f"Bus: {counts['bus']}",
        f"Van: {counts['van']}",
    ]

    for i, text in enumerate(legend_text):
        cv2.putText(
            img_bgr,
            text,
            (legend_x, legend_y + i * line_height),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )


    # Convert back to RGB for output
    annotated_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return annotated_rgb


def video_inference(video_path, conf_thres: float = 0.01):

    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video")

    # Set default FPS if not available
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps is None or fps == 0:
        fps = 30

    # Set video properties
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Output file (MP4)
    import tempfile
    output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = output_file.name
    output_file.close()

    # H.264 Codec
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not writer.isOpened():
        raise RuntimeError("VideoWriter failed to open. Codec not supported.")


    # Store per-frame counts for dashboard
    frame_idx = 0
    timeline_counts = []  # list of dicts: {"t": time_in_sec, "car": x, "bus": y, "van": z}


    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert each frame for YOLO
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Inference
        results = model(frame_rgb)[0]


        # Vehicle counts for this frame
        counts = {"car": 0, "bus": 0, "van": 0}


        # Draw boxes and count vehicles
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf < conf_thres:
                continue

            # Extract box coordinates and class
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0])
            cls_name = results.names[cls_id]

            # Update counts
            if cls_name in counts:
                counts[cls_name] += 1

            label = f"{cls_name} {conf:.2f}"

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Label box
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - th - 4), (x1 + tw, y1), (0, 255, 0), -1)
            cv2.putText(frame, label, (x1, y1 - 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 0), 1)


        # Store counts for this frame for dashboard use
        t_sec = frame_idx / fps
        timeline_counts.append({
            "t": t_sec,
            "car": counts["car"],
            "bus": counts["bus"],
            "van": counts["van"],
        })
        frame_idx += 1


        # Draw legend (bottom-left)
        legend_x = 10
        legend_y = frame.shape[0] - 90
        line_height = 26

        legend_text = [
            "Vehicle Counts:",
            f"Car: {counts['car']}",
            f"Bus: {counts['bus']}",
            f"Van: {counts['van']}",
        ]

        for i, text in enumerate(legend_text):
            cv2.putText(
                frame,
                text,
                (legend_x, legend_y + i * line_height),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

        # Write final frame
        writer.write(frame)

    cap.release()
    writer.release()

    return output_path, timeline_counts

