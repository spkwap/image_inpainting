from flask import Flask, jsonify
import os
import subprocess
from PIL import Image
import numpy as np
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from forms import RegistrationForm, LoginForm
from models import db, User, UserImage
from app import db
from flask import send_file
import base64
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from io import BytesIO


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = 'data/uploads'
RESULTS_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('home')) if current_user.is_authenticated else redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('upload.html', username=current_user.username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully, you can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout.', 'info')
    return redirect(url_for('login'))

@app.route('/gallery')
@login_required
def gallery():
    images = UserImage.query.filter(UserImage.user_id == current_user.id).all()
    image_data_list = [
        {'id': image.id, 'filename': image.filename, 'data': base64.b64encode(image.image_data).decode('utf-8')}
        for image in images
    ]
    return render_template('gallery.html', images=image_data_list)


@app.route('/delete_image/<int:image_id>', methods=['POST'])
@login_required
def delete_image(image_id):
    image = UserImage.query.filter_by(id=image_id, user_id=current_user.id).first()
    if not image:
        flash('Image not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('gallery'))

    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('gallery'))

@app.route('/download_image/<int:image_id>', methods=['POST'])
def download_image(image_id):
    image = UserImage.query.get(image_id)

    if image is None:
        return "Image not found", 404

    image_data = image.image_data
    image_io = BytesIO(image_data)

    return send_file(image_io, mimetype='image/jpeg', as_attachment=True, download_name=image.filename)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    image_count = UserImage.query.filter_by(user_id=current_user.id).count()

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')

        if check_password_hash(current_user.password, current_password):
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Password is changed!', 'success')
        else:
            flash('Old password is incorrect!', 'danger')

    return render_template('profile.html', user=current_user, image_count=image_count)



def ensure_binary_mask(mask_np):

    mask_np[mask_np <= 20] = 0

    mask_np[mask_np > 20] = 255
    return mask_np




@app.route('/inpaint', methods=['POST'])
def inpaint():
    image_file = request.files['image']
    model_name = request.form.get('model')

    if not model_name or model_name not in ['places2.pth', 'celeba.pth', 'psv.pth']:
        return jsonify({'error': 'Invalid model selected.'}), 400

    image_extension = image_file.filename.split('.')[-1].lower()
    if image_extension not in ['jpg', 'jpeg', 'png']:
        return jsonify({'error': 'Only jpg, jpeg, or png images are allowed.'}), 400

    image_path = os.path.join(UPLOAD_FOLDER, f'input_image.{image_extension}')
    image_file.save(image_path)

    try:
        image = Image.open(image_path).convert("RGB")
        original_size = image.size
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
            ['python', 'src/test.py', '--list_file', list_file_path, '--snapshot', f'data/{model_name}'],
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

    try:
        with Image.open(result_path) as result_image:
            resized_image = result_image.resize(original_size, Image.LANCZOS)
            resized_image.save(result_path)
    except FileNotFoundError:
        return jsonify({'error': 'Result file not found'}), 404

    try:
        with open(result_path, 'rb') as f:
            image_data = f.read()

        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
        new_filename = f"Photo saved {current_time}"

        if current_user.is_authenticated:
            user_instance = User.query.get(current_user.id)
            new_image = UserImage(filename=new_filename, image_data=image_data, user=user_instance)
        else:
            return "User not authenticated", 401

        db.session.add(new_image)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': f'Failed to save the result: {e}'}), 500

    return send_file(result_path, mimetype=f'image/{image_extension}')



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
