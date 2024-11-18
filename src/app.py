from flask import Flask, request, render_template, jsonify, send_file
import os
import subprocess
from PIL import Image
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'data/uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('upload.html')

# Funkcja wymuszająca, aby maska miała tylko piksele czarne i białe
def ensure_binary_mask(mask_np):
    """
    Zamienia piksele na czarne (0) lub białe (255) w masce.
    """
    # Jeśli wartość jest bliska czarnego, ustaw na czarny (0)
    mask_np[mask_np <= 20] = 0
    # Wszystkie inne ustaw na biały (255)
    mask_np[mask_np > 20] = 255
    return mask_np

def resize_mask(mask_image, target_size=(512, 512)):
    """
    Skaluje obraz maski do rozmiaru 512x512 pikseli.
    """
    return mask_image.resize(target_size, Image.ANTIALIAS)

@app.route('/inpaint', methods=['POST'])
def inpaint():
    # Pobierz obrazek użytkownika
    image_file = request.files['image']
    image_extension = image_file.filename.split('.')[-1].lower()

    if image_extension not in ['jpg', 'jpeg', 'png']:
        return jsonify({'error': 'Only jpg, jpeg, or png images are allowed.'}), 400

    # Zapisz obrazek
    image_path = os.path.join(UPLOAD_FOLDER, f'input_image.{image_extension}')
    image_file.save(image_path)

    # Otwórz obrazek i utwórz maskę na podstawie białych pikseli
    image = Image.open(image_path).convert("RGB")  # Konwersja do RGB
    image_np = np.array(image)

    # Tworzymy maskę: białe obszary (255, 255, 255) stają się czarne (0), reszta biała (255)
    mask = (~np.all(image_np == [255, 255, 255], axis=-1)).astype(np.uint8) * 255

    # Korekta maski do binarycznej
    mask = ensure_binary_mask(mask)

    # Przekształcenie maski do obrazu w skali szarości
    mask_image = Image.fromarray(mask, mode='L')  # Użycie trybu 'L' dla skali szarości

    # Skalowanie maski do rozmiaru 512x512
    #mask_image = resize_mask(mask_image, target_size=(512, 512))

    # Konwertowanie maski do 32-bitowego formatu (RGBA)
    mask_image = mask_image.convert("RGBA")

    # Zapisz maskę
    mask_path = os.path.join(UPLOAD_FOLDER, f'input_mask.{image_extension}')
    mask_image.save(mask_path)

    # Przygotuj plik 'places2_example_list'
    list_file_path = 'places2_example_list'
    with open(list_file_path, 'w') as f:
        image_path = image_path.replace("\\", "/")
        mask_path = mask_path.replace("\\", "/")
        f.write(f"{image_path}\t{mask_path}\n")

    try:
        result = subprocess.run(
            ['python', 'src/test.py', '--list_file', list_file_path, '--snapshot', 'data/places2.pth'],
            check=True, capture_output=True, text=True
        )

        print("stdout:", result.stdout)
        print("stderr:", result.stderr)

    except subprocess.CalledProcessError as e:
        return jsonify({
            'error': f"Inpainting script failed. Return code: {e.returncode}, "
                     f"stdout: {e.stdout}, stderr: {e.stderr}"
        }), 500

    # Aktualizacja ścieżki result_path, aby wskazywała na plik w folderze 'results'
    result_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        'results', f'input_image.{image_extension}'
    )

    return send_file(result_path, mimetype=f'image/{image_extension}')

if __name__ == '__main__':
    app.run(debug=True)
