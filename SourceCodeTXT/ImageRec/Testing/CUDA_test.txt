"""
This script is used to verify the CUDA setup on a machine,
ensuring that PyTorch can utilize GPU resources for faster inferencing.
"""

import torch

# Check if CUDA is available on the system
print(torch.cuda.is_available())

# Print the number of CUDA-capable devices
print(torch.cuda.device_count())

# Print the name of the first CUDA device
print(torch.cuda.get_device_name(0))