import os
import platform
import torch
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from distutils.sysconfig import get_config_vars

(opt,) = get_config_vars("OPT")

if opt:
    os.environ["OPT"] = " ".join(
        flag for flag in opt.split() if flag != "-Wstrict-prototypes"
    )

src = "src"
sources = [
    os.path.join(root, file)
    for root, dirs, files in os.walk(src)
    for file in files
    if file.endswith(".cpp") or file.endswith(".cu")
]

# Define the CUDA extension
cuda_extension = CUDAExtension(
    name="pointops._C",
    sources=sources,
    extra_compile_args={
        "cxx": ["-g"],
        "nvcc": [
            "-O2",
            "-arch=sm_75",
            "-arch=sm_80",
            "-arch=sm_86",
            "-arch=sm_87",
            "-arch=sm_89",      # Ada Lovelace
            "-arch=sm_90",      # Hopper
            "-arch=sm_120",     # Future architecture
        ],
    },
)

setup(
    name="pointops",
    version="1.0",
    install_requires=["torch", "numpy"],
    packages=["pointops"],
    package_dir={"pointops": "functions"},
    ext_modules=[cuda_extension],
    cmdclass={"build_ext": BuildExtension},
)
