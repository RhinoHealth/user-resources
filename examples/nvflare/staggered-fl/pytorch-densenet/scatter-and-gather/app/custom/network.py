import torch.nn as nn
import torchvision


class DenseNetPneumonia(nn.Module):
    """DenseNet-121 with a two-class (normal / pneumonia) head.

    With `pretrained=True` it starts from the ImageNet weights, which the Dockerfile downloads into `TORCH_HOME` at
    build time because FL pods may have no internet access.
    """

    def __init__(self, num_classes: int = 2, pretrained: bool = True):
        super().__init__()
        self.model = torchvision.models.densenet121(weights="DEFAULT" if pretrained else None)
        self.model.classifier = nn.Linear(self.model.classifier.in_features, num_classes)

    def forward(self, x):
        return self.model(x)
