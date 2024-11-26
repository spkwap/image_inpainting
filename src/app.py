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


def ensure_binary_mask(mask_np):
    """
    Zamienia piksele na czarne (0) lub białe (255) w masce.
    """

    mask_np[mask_np <= 20] = 0

    mask_np[mask_np > 20] = 255
    return mask_np

@app.route('/inpaint', methods=['POST'])
def inpaint():

    image_file = request.files['image']
    image_extension = image_file.filename.split('.')[-1].lower()

    if image_extension not in ['jpg', 'jpeg', 'png']:
        return jsonify({'error': 'Only jpg, jpeg, or png images are allowed.'}), 400


    image_path = os.path.join(UPLOAD_FOLDER, f'input_image.{image_extension}')
    image_file.save(image_path)

    try:

        image = Image.open(image_path).convert("RGB")
        image.save(image_path)
    except Exception as e:
        return jsonify({'error': f'Failed to process the uploaded image: {e}'}), 500


    try:
        image_np = np.array(image)

        mask = (~np.all(image_np == [255, 255, 255], axis=-1)).astype(np.uint8) * 255
        mask_image = Image.fromarray(mask, mode='L')


        mask_path = os.path.join(UPLOAD_FOLDER, f'input_mask.{image_extension}')
        mask_image.save(mask_path)
    except Exception as e:
        return jsonify({'error': f'Failed to generate or save the mask: {e}'}), 500


    list_file_path = 'places2_example_list'
    try:
        with open(list_file_path, 'w') as f:
            image_path = image_path.replace("\\", "/")
            mask_path = mask_path.replace("\\", "/")
            f.write(f"{image_path}\t{mask_path}\n")
    except Exception as e:
        return jsonify({'error': f'Failed to prepare the example list file: {e}'}), 500


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


    result_path = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        'results', f'input_image.{image_extension}'
    )


    return send_file(result_path, mimetype=f'image/{image_extension}')


if __name__ == '__main__':
    app.run(debug=True)
