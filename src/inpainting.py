import torch
from model import load_model
from utils import preprocess_image, postprocess_image


def perform_inpainting(image_path, mask_path, channel_order="RGB"):
    model = load_model()
    image_tensor = preprocess_image(image_path, channel_order)
    mask_tensor = preprocess_image(mask_path, channel_order)

    with torch.no_grad():
        output_tensor = model(image_tensor, mask_tensor)

    # Ensure the output has the correct dimensions
    if isinstance(output_tensor, list):
        output_tensor = torch.stack(output_tensor)
    output_tensor = output_tensor.squeeze()
    while output_tensor.dim() > 3:
        output_tensor = output_tensor[0]

    return postprocess_image(output_tensor)
