import cv2
import numpy as np
import os
import pandas as pd


def calculate_psnr(original, filtered):
    mse = np.mean((original - filtered) ** 2)
    if mse == 0:
        return float('inf')
    psnr = 10 * np.log10(255 ** 2 / mse)
    return round(psnr, 4)



def apply_median_filter(image, kernel_size=5):
    return cv2.medianBlur(image, kernel_size)


def apply_vmf_filter(image, kernel_size=5):
    pad_size = kernel_size // 2
    padded_image = cv2.copyMakeBorder(image, pad_size, pad_size, pad_size, pad_size, cv2.BORDER_REFLECT)
    vmf_image = np.zeros_like(image)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            neighborhood = padded_image[i:i + kernel_size, j:j + kernel_size]
            pixels = neighborhood.reshape(-1, 3)
            median_pixel = np.median(pixels, axis=0)
            closest_pixel = pixels[np.argmin(np.sum((pixels - median_pixel) ** 2, axis=1))]
            vmf_image[i, j] = closest_pixel

    return vmf_image




folder_path = 'data'
original_cases = ['case1', 'case2', 'case3']
noise_levels = ['5', '10', '20']

results = []

for case in original_cases:
    original_image_path = os.path.join(folder_path, f"{case}.png")
    original_image = cv2.imread(original_image_path)

    for noise_level in noise_levels:
        noisy_image_path = os.path.join(folder_path, f"{case}_noisy_{noise_level}.png")
        noisy_image = cv2.imread(noisy_image_path)

        if original_image is None or noisy_image is None:
            print(f"Nie udało się wczytać obrazu dla {case} z poziomem szumu {noise_level}.")
            continue

        median_filtered = apply_median_filter(noisy_image)
        psnr_median = calculate_psnr(original_image, median_filtered)

        vmf_filtered = apply_vmf_filter(noisy_image)
        psnr_vmf = calculate_psnr(original_image, vmf_filtered)

        inpainting_image_path = os.path.join(folder_path, f"{case}_{noise_level}_places.png")
        inpainting_image = cv2.imread(inpainting_image_path)

        if inpainting_image is not None:
            psnr_inpainting = calculate_psnr(original_image, inpainting_image)
        else:
            psnr_inpainting = None
            print(f"Nie udało się wczytać obrazu po inpaintingu dla {case} z poziomem szumu {noise_level}.")

        results.append({
            "Obraz": case,
            "Poziom szumu [%] ": noise_level,
            "Filtr medianowy [dB]": psnr_median,
            "VMF [dB]": psnr_vmf,
            "Inpainting [dB]": psnr_inpainting
        })

df = pd.DataFrame(results)
df.to_csv("psnr_results.csv", index=False, encoding='utf-8')
print("Tabela wyników PSNR została zapisana jako 'psnr_results.csv'.")
