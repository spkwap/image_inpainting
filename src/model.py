import torch
from net import MADFNet


class Args:
    def __init__(self):
        self.n_refinement_D = 1
        self.upsampling = 'bilinear'


def load_model():
    args = Args()

    model = MADFNet(args)

    checkpoint = torch.load("data/places2.pth", map_location="cpu", weights_only=True)

    model.load_state_dict(checkpoint['model'], strict=False)

    model.eval()

    return model
