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

# Conditionally set the conda_lib_path for Windows
conda_lib_path = None
if platform.system() == "Windows":
    conda_lib_path = os.path.join(sys.prefix, 'Library', 'lib')
    torch_lib_dir = os.path.join(os.path.dirname(torch.__file__), 'lib')

# Define the CUDA extension
cuda_extension = CUDAExtension(
    name="pointops._C",
    sources=sources,
    extra_compile_args={"cxx": ["-g"], "nvcc": ["-O2", "-gencode=arch=compute_75,code=sm_75",]},
)

# If conda_lib_path is set, add it to the library_dirs
if conda_lib_path:
    cuda_extension.library_dirs = [conda_lib_path, torch_lib_dir]

setup(
    name="pointops",
    version="1.0",
    install_requires=["torch", "numpy"],
    packages=["pointops"],
    package_dir={"pointops": "functions"},
    ext_modules=[cuda_extension],
    cmdclass={"build_ext": BuildExtension},
)
