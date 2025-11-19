from ultralytics import YOLO
import torch
from pathlib import Path
import os


# training_path = "~/Documents/vehicle-detection.v1i.yolov12"
# p = Path(training_path).expanduser()

path = r"C:\Users\aam71\Desktop\vehicle-detection.v1i.yolov12"
data_yaml_path = os.path.join(path, "data.yaml")


# Once ran, this return the following results:
# {'bus': 2293, 'car': 4743, 'van': 2167, 'empty': 15}
# This shows that the dataset is imbalanced, with very few 'empty' labels.
def check_dataset():
    classes = ['bus', 'car', 'van', 'empty']
    class_counts = {
        'bus': 0,
        'car': 0,
        'van': 0,
        'empty': 0
    }

    for file_path in p.glob('train/labels/*.txt'):
        # print(file_path)
        try:
            _file = open(file_path)
            _class = _file.read(1)
            try:
                _class = int(_class)
            except:
                _class = 3
            class_counts[classes[_class]] += 1

        except Exception as e:
            print(f">> Experienced the following error: {e}")

    print(class_counts)



if __name__ == "__main__":
    # print("Checking dataset class distribution...")

    # I wont do any data augmentation since the dataset is already heavily augmented.
    # If I did, I would risk overfitting to the augmented data. Or augmenting already augmented data, creating unrealistic samples.
    # Hence, I proceed to train the model using oversampling of the minority classes ('van' and 'bus') to balance the class representation.
    # ONLY IF the baseline model does not perform well.

    # Make GPU the default if available
    if torch.cuda.is_available():
        device = 0  # GPU 0
        print(f"Using CUDA device: {torch.cuda.get_device_name(device)}")
    else:
        device = "cpu"
        print("CUDA not available, using CPU.")

    # Load pre-trained YOLOv12 medium model
    model = YOLO("yolo12s.pt")

    # --- SAFER SETTINGS FOR GTX 1650 (4GB-ish VRAM) | With consultation from ChatGPT ---
    EPOCHS = 30       # start with 50 to test; increase to 80–100 later
    IMG_SIZE = 512    # 640, standard for YOLO
    BATCH = 8         # safer than 16 for a 1650

    results = model.train(
        data=data_yaml_path,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH,
        name="vehicle-detection/baseline_model_gtx1650_12s",
        device=device,       # use GPU 0
        workers=4,           # use 2 to reduce dataloader workers to keep system smooth
        cache=False,         # keep RAM usage sane
        exist_ok=True,       # overwrite if folder exists
    )

    print("Training finished. Best weights saved to:", results.save_dir)