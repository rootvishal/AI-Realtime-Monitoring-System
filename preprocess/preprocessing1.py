import cv2
import numpy as np
import os

# Denoise the image
def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, h=10, templateWindowSize=7)


# Sharpen the image
def sharpen_image(image):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)

# Normalize lighting
def normalize_lighting(image):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    normalized_image = cv2.merge((l, a, b))
    return cv2.cvtColor(normalized_image, cv2.COLOR_LAB2BGR)

# Resize image with padding
def resize_with_padding(image, target_size=(224, 224)):
    h, w = image.shape[:2]
    scale = min(target_size[0] / h, target_size[1] / w)
    resized = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    
    top = (target_size[0] - resized.shape[0]) // 2
    bottom = target_size[0] - resized.shape[0] - top
    left = (target_size[1] - resized.shape[1]) // 2
    right = target_size[1] - resized.shape[1] - left
    
    return cv2.copyMakeBorder(resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[0, 0, 0])

# Detect if the image is blurry
def is_blurry(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold

# Preprocess a single image
def preprocess_image(image_path, output_path, target_size=(224, 224), blur_threshold=100):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Cannot read image: {image_path}")
        return

    if is_blurry(img, blur_threshold):
        print(f"Skipping blurry image: {image_path}")
        return

    img = denoise_image(img)
    img = sharpen_image(img)
    img = normalize_lighting(img)
    img = resize_with_padding(img, target_size=target_size)
    
    cv2.imwrite(output_path, img)

# Preprocess all images in a dataset
def preprocess_dataset(input_dir, output_dir, target_size=(224, 224), blur_threshold=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for person_folder in os.listdir(input_dir):
        person_folder_path = os.path.join(input_dir, person_folder)

        # Only process if it's a folder
        if os.path.isdir(person_folder_path):
            for filename in os.listdir(person_folder_path):
                # Check if the file is an image (you can add more formats if needed)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    input_path = os.path.join(person_folder_path, filename)
                    output_path = os.path.join(output_dir, person_folder + "_" + filename)
                    preprocess_image(input_path, output_path, target_size=target_size, blur_threshold=blur_threshold)

# Example usage
input_dir = r"c:\Users\kisho\Downloads\P3\dataset\augmented"  # Ensure this path is correct
output_dir = r"C:\Users\kisho\Downloads\P3\dataset"  # Ensure this path is correct
preprocess_dataset(input_dir, output_dir)
