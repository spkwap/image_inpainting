import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
#import opt

# Wartości MEAN i STD dla normalizacji obrazu w standardzie ImageNet
MEAN = [0.485, 0.456, 0.406]  # Średnia dla normalizacji
STD = [0.229, 0.224, 0.225]  # Odchylenie standardowe dla normalizacji


def preprocess_image(image_path, channel_order=['R', 'G', 'B']):
    image = Image.open(image_path)

    # Wyświetlenie pierwszych 1000 pikseli przed przetworzeniem
    image_np = np.array(image)
    print(f"First 50 pixel values from original image (before processing):")
    print(image_np.flatten()[:50])

    channels = image.split()

    # Tworzymy mapowanie od nazw kanałów ('R', 'G', 'B') do indeksów kanałów
    channel_indices = {'R': 0, 'G': 1, 'B': 2}

    # Zmiana kolejności kanałów na podstawie channel_order
    image = Image.merge("RGB", (channels[channel_indices[channel_order[0]]],
                                channels[channel_indices[channel_order[1]]],
                                channels[channel_indices[channel_order[2]]]))

    preprocess = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=opt.MEAN, std=opt.STD)
    ])
    tensor = preprocess(image).unsqueeze(0)  # Dodanie wymiaru partii

    # Wyświetlenie pierwszych 1000 pikseli po przetworzeniu
    tensor_np = tensor.squeeze().cpu().numpy()
    print(f"First 50 pixel values after preprocessing (tensor):")
    print(tensor_np.flatten()[:50])

    return tensor


def postprocess_image(tensor):
    tensor = tensor.squeeze(0)  # Usuwamy wymiar partii, jeśli istnieje

    # Sprawdzenie kształtu tensoru
    print(f"Tensor shape before processing: {tensor.shape}")

    # Wyświetlenie wartości tensoru (pierwsze 1000 pikseli przed przetworzeniem)
    print(f"First 50 values before processing:")
    print(tensor.flatten()[:50])

    if len(tensor.shape) != 3 or tensor.shape[0] != 3:
        print(f"Tensor shape is not in expected format: {tensor.shape}")
        return None  # Zwróć None lub odpowiedni komunikat, jeśli kształt jest niepoprawny

    # Sprawdź wartości po permutacji
    tensor = tensor.permute(1, 2, 0).clamp(0, 1) * 255.0  # Transponujemy i przywracamy wartość w zakresie 0-255
    print(f"Tensor values after processing (first 1000 pixels):")
    print(tensor.flatten()[:50])

    # Przeniesienie na CPU przed konwersją
    tensor = tensor.cpu().numpy()

    # Sprawdzenie rozmiaru obrazu
    print(f"Image shape before creating PIL image: {tensor.shape}")

    # Wyświetlenie pierwszych 1000 pikseli po przetworzeniu
    print(f"First 50 pixels after processing:")
    print(tensor.flatten()[:50])

    # Konwersja na obraz
    try:
        image = Image.fromarray(tensor.astype('uint8'))  # Zmiana typu na unsigned byte
        print(f"Image size: {image.size}")
        image_np = np.array(image)
        print(f"First 50 pixels of the picture i display on site:")
        print(image_np.flatten()[:50])
        return image
    except Exception as e:
        print(f"Error converting tensor to image: {e}")
        return None


def unnormalize(x):
    """
    Funkcja unormalizacji dla obrazu.
    """
    x = x.transpose(1, 3)  # Zmieniamy wymiary na [N, H, W, C]
    x = x * torch.Tensor(STD).view(1, 1, 1, 3) + torch.Tensor(MEAN).view(1, 1, 1, 3)  # Odwracamy normalizację
    x = x.transpose(1, 3)  # Przywracamy wymiary na [N, C, H, W]
    return x
