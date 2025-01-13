import cv2
import numpy as np
import os

def add_salt_and_pepper_noise(image, noise_level):
    row, col, ch = image.shape
    total_pixels = row * col

    num_salt = int(total_pixels * noise_level / 2 / 100)
    num_pepper = int(total_pixels * noise_level / 2 / 100)

    noisy_image = image.copy()

    salt_coords = [np.random.randint(0, i - 1, num_salt) for i in image.shape[:2]]
    noisy_image[salt_coords[0], salt_coords[1], :] = 255

    pepper_coords = [np.random.randint(0, i - 1, num_pepper) for i in image.shape[:2]]
    noisy_image[pepper_coords[0], pepper_coords[1], :] = 0

    return noisy_image

def generate_noisy_images(image):
    noise_levels = [5, 10, 20]
    noisy_images = []

    for level in noise_levels:
        noisy_image = add_salt_and_pepper_noise(image, level)
        noisy_images.append(noisy_image)

    return noisy_images

folder_path = 'data'

image_files = ['case1.png', 'case2.png', 'case3.png']

for image_file in image_files:
    image_path = os.path.join(folder_path, image_file)
    image = cv2.imread(image_path)

    if image is not None:
        noisy_images = generate_noisy_images(image)

        for idx, noisy_image in enumerate(noisy_images):
            noise_level = [5, 10, 20][idx]
            filename = f'{os.path.splitext(image_file)[0]}_noisy_{noise_level}.png'
            save_path = os.path.join(folder_path, filename)
            cv2.imwrite(save_path, noisy_image)
            print(f"Zapisano: {save_path}")

    else:
        print(f"Nie udało się wczytać obrazu: {image_path}")
