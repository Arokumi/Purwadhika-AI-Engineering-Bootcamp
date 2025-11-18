from ultralytics import YOLO
from pathlib import Path
import os


training_path = "~/Documents/vehicle-detection.v1i.yolov12"
p = Path(training_path).expanduser()


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
    # check_dataset() | Already run


    # We wont do any data augmentation since the dataset is already heavily augmented.
    # If we did, we would risk overfitting to the augmented data. Or augmenting already augmented data, creating unrealistic samples.
    # Hence, we proceed to train the model using oversampling of the minority classes ('van' and 'bus') to balance the class representation.





    # Train the model
    model = YOLO("yolo12m.pt")

    results = model.train(
        data="vehicle-detection.v1i.yolov12/data.yaml",
        epochs=100,
        imgsz=640,
        batch=16,
        name="vehicle-detection.v1i.yolov12/exp1",
    )