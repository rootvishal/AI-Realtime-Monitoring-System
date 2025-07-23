import os
import cv2

def resize_dataset(input_dir, output_dir, size=(512, 512)):
    """
    Resize all images in a dataset directory with class-wise subfolders.

    Args:
        input_dir (str): Path to the dataset directory (contains class subfolders).
        output_dir (str): Path to save the resized images (maintains class subfolders).
        size (tuple): Target size for resizing images, e.g., (224, 224).
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate over each class folder in the input directory
    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        
        # Skip non-directory entries
        if not os.path.isdir(class_path):
            continue

        # Create corresponding class folder in the output directory
        output_class_path = os.path.join(output_dir, class_name)
        if not os.path.exists(output_class_path):
            os.makedirs(output_class_path)

        # Process each image in the class folder
        for filename in os.listdir(class_path):
            file_path = os.path.join(class_path, filename)

            # Check if the file is an image
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Read the image
                    img = cv2.imread(file_path)

                    # Check if the image was read successfully
                    if img is None:
                        print(f"Failed to read {file_path}. Skipping...")
                        continue

                    # Resize the image
                    resized_img = cv2.resize(img, size)

                    # Save the resized image to the corresponding output directory
                    output_file_path = os.path.join(output_class_path, filename)
                    cv2.imwrite(output_file_path, resized_img)
                    print(f"Resized and saved: {output_file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
            else:
                print(f"Skipping non-image file: {file_path}")

# Example usage
if __name__ == "__main__":
    input_dir = r"C:\Project_version_1\stddata"  # Replace with your dataset directory
    output_dir = r"C:\Project_version_1\process data\resize"  # Replace with your output directory
    target_size = (512, 512)  # Specify the target size

    resize_dataset(input_dir, output_dir, target_size)
    print("Dataset resizing completed!")
