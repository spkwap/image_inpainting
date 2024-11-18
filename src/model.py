import torch
from net import MADFNet


class Args:
    def __init__(self):
        self.n_refinement_D = 1  # Zgodnie z wymaganiami modelu
        self.upsampling = 'bilinear'  # lub 'nearest' w zależności od potrzeby


def load_model():
    # Tworzymy instancję args
    args = Args()

    # Tworzymy model
    model = MADFNet(args)

    # Ładujemy wagi modelu, ignorując brakujące i nieznane klucze
    checkpoint = torch.load("data/places2.pth", map_location="cpu", weights_only=True)

    model.load_state_dict(checkpoint['model'], strict=False)

    # Ustawiamy model w tryb ewaluacji
    model.eval()

    return model
