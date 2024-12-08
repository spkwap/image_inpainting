# Image Inpainting Project

This project implements an image inpainting application using a pretrained neural network model. Users can upload an image, draw a mask to indicate the area they want to inpaint, and the application will recreate the image without the masked area.

## Features

- Upload images
- Draw masks on images
- Repaint images using a neural network model from https://github.com/MADF-inpainting/Pytorch-MADF

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/spkwap/image_inpainting.git
   cd image_inpainting

2. Save file places2.pth from this link: [https://drive.google.com/file/d/10iXhPEiOiNzTbM-Yc1GRy2-D9Xjmd1cI/view](https://drive.google.com/file/d/10iXhPEiOiNzTbM-Yc1GRy2-D9Xjmd1cI/view) in data folder
3. Save file celeba.pth from this link: [https://drive.google.com/file/d/10iXhPEiOiNzTbM-Yc1GRy2-D9Xjmd1cI/view](https://drive.google.com/file/d/1kWV_RT6xTXuyIh7Oj3OnoZGOB9h4ZP0Z/view) in data folder
4. Save file psv.pth from this link: [https://drive.google.com/file/d/10iXhPEiOiNzTbM-Yc1GRy2-D9Xjmd1cI/view](https://drive.google.com/file/d/1cmrj_zod5eCsMavLVC4BGr9KavHXizkw/view) in data folder

5. To start an app
   ```bash
   python src/app.py
