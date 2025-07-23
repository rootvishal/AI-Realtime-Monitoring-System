import os
import cv2
import numpy as np
from keras.preprocessing.image import ImageDataGenerator
from tqdm import tqdm


def augment_images(input_dir, output_dir, num_augmented=20, image_size=(512, 512)):
    """
    Augment images while preserving clarity and saving them to the output directory.
    Args:
        input_dir (str): Path to the dataset directory with class-wise subfolders.
        output_dir (str): Path to save the augmented images.
        num_augmented (int): Number of augmented images per original image.
        image_size (tuple): Target image size (e.g., (512, 512)).
    """
    # Data augmentation generator with clarity-preserving transformations
    datagen = ImageDataGenerator(
        rotation_range=15,  # Slight rotations to avoid distortion
        width_shift_range=0.1,  # Small width shift
        height_shift_range=0.1,  # Small height shift
        brightness_range=[0.8, 1.2],  # Brightness adjustments
        zoom_range=0.1,  # Small zoom in/out
        horizontal_flip=True,  # Horizontal flip
        fill_mode='reflect'  # Reflect to avoid black borders
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
                try:
                    img = cv2.imread(file_path)
                    if img is None:
                        print(f"Failed to read {file_path}. Skipping...")
                        continue

                    img = cv2.resize(img, image_size)  # Resize to 512x512
                    img_array = np.expand_dims(img, axis=0)

                    i = 0
                    for batch in datagen.flow(img_array, batch_size=1, save_to_dir=output_class_path,
                                              save_prefix=filename.split('.')[0], save_format='jpg'):
                        i += 1
                        if i >= num_augmented:
                            break
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")


def main():
    input_dir = r"C:\Project_version_1\process data\resize"  # Path to original dataset
    augmented_dir = r"C:\Project_version_1\process data\argumented"  # Path for augmented dataset
    image_size = (512, 512)  # Target size for resizing images

    # Augment images
    print("Starting image augmentation...")
    augment_images(input_dir, augmented_dir, num_augmented=20, image_size=image_size)
    print("Image augmentation completed successfully!")


if __name__ == "__main__":
    main()
