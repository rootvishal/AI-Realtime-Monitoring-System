import os
import cv2
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from tqdm import tqdm

def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

def sharpen_image(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

def augment_images(input_dir, output_dir, num_augmented=50, image_size=(224, 224)):
    datagen = ImageDataGenerator(
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
        brightness_range=(0.8, 1.2),
        fill_mode='reflect'
    )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_path):
            continue
        
        output_class_path = os.path.join(output_dir, class_name)
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)
        
        for filename in tqdm(os.listdir(class_path), desc=f"Augmenting {class_name}"):
            file_path = os.path.join(class_path, filename)
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = cv2.imread(file_path)
                if img is None:
                    continue
                img = cv2.resize(img, image_size)
                img = sharpen_image(img)
                
                img_array = np.expand_dims(img, axis=0)
                i = 0
                for batch in datagen.flow(img_array, batch_size=1):
                    augmented_img = batch[0].astype('uint8')
                    if not is_blurry(augmented_img):
                        save_path = os.path.join(output_class_path, f"{filename.split('.')[0]}_aug_{i}.jpg")
                        cv2.imwrite(save_path, augmented_img)
                        i += 1
                    if i >= num_augmented:
                        break

# Usage
input_dir = r"C:\Users\kisho\Downloads\P3\dataset\train"  # Original dataset
output_dir = r"C:\Users\kisho\Downloads\P3\dataset\augmented"  # Augmented dataset
augment_images(input_dir, output_dir, num_augmented=50)
