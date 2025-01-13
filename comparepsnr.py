import cv2
from skimage.metrics import peak_signal_noise_ratio as psnr


def compare_images_psnr(image_path_1, image_path_2):

    try:
        image1 = cv2.imread(image_path_1, cv2.IMREAD_GRAYSCALE)
        image2 = cv2.imread(image_path_2, cv2.IMREAD_GRAYSCALE)

        if image1 is None or image2 is None:
            raise ValueError("Nie udało się wczytać jednego z obrazów. Sprawdź ścieżki plików.")

        if image1.shape != image2.shape:
            raise ValueError("Obrazy mają różne rozmiary i nie mogą zostać porównane.")

        psnr_value = psnr(image1, image2)
        return psnr_value

    except Exception as e:
        print(f"Błąd podczas porównywania obrazów: {e}")
        return None


# Główna część skryptu
if __name__ == "__main__":
    image_path_1 = "src/doroad.png"
    image_path_2 = "results/original_image.png"

    psnr_value = compare_images_psnr(image_path_1, image_path_2)

    # Wyświetlenie wyniku
    if psnr_value is not None:
        print(f"PSNR między obrazami {image_path_1} i {image_path_2} wynosi: {psnr_value:.2f} dB")
    else:
        print("Nie udało się porównać obrazów.")
