import logging

import torch

logger = logging.getLogger(__name__)


def get_device() -> torch.device:
    """
    Определить доступное устройство для вычислений (GPU или CPU)

    Returns:
        torch.device: torch.device("cuda") если GPU доступна, иначе torch.device("cpu")
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        logger.info(f"✅ [device] GPU доступна: {gpu_name}")
    else:
        logger.info("ℹ️ [device] GPU недоступна, используется CPU")
        device = torch.device("cpu")
    return device
