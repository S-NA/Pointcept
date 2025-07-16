import os
import platform
import sys
import torch
from sys import argv
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
from distutils.sysconfig import get_config_vars

(opt,) = get_config_vars("OPT")
if opt:
    os.environ["OPT"] = " ".join(
        flag for flag in opt.split() if flag != "-Wstrict-prototypes"
    )


def _argparse(pattern, argv, is_flag=True, is_list=False):
    if is_flag:
        found = pattern in argv
        if found:
            argv.remove(pattern)
        return found, argv
    else:
        arr = [arg for arg in argv if pattern == arg.split("=")[0]]
        if is_list:
            if len(arr) == 0:  # not found
                return False, argv
            else:
                assert "=" in arr[0], f"{arr[0]} requires a value."
                argv.remove(arr[0])
                val = arr[0].split("=")[1]
                if "," in val:
                    return val.split(","), argv
                else:
                    return [val], argv
        else:
            if len(arr) == 0:  # not found
                return False, argv
            else:
                assert "=" in arr[0], f"{arr[0]} requires a value."
                argv.remove(arr[0])
                return arr[0].split("=")[1], argv


INCLUDE_DIRS, argv = _argparse("--include_dirs", argv, False, is_list=True)
include_dirs = []
if not (INCLUDE_DIRS is False):
    include_dirs += INCLUDE_DIRS

if platform.system() == "Windows":
    # Get the base path of the current Conda environment
    base_path = sys.prefix

    # Create the full path to the 'windows' include directory
    include_windows_path = os.path.join(base_path, 'Library', 'include', 'windows')
    include_dirs.append(include_windows_path) # sparsehash nonsense
    conda_lib_path = os.path.join(sys.prefix, 'Library', 'lib')
    print('='*20)
    print(conda_lib_path)
    torch_lib_dir = os.path.join(os.path.dirname(torch.__file__), 'lib')

setup(
    name="pointgroup_ops",
    packages=["pointgroup_ops"],
    package_dir={"pointgroup_ops": "functions"},
    install_requires=["torch"],
    ext_modules=[
        CUDAExtension(
            name="pointgroup_ops_cuda",
            sources=["src/bfs_cluster.cpp", "src/bfs_cluster_kernel.cu"],
            library_dirs=[conda_lib_path, torch_lib_dir],
            extra_compile_args={"cxx": ["-g"], "nvcc": ["-O2", "-gencode=arch=compute_75,code=sm_75",]},
        )
    ],
    include_dirs=[*include_dirs],
    cmdclass={"build_ext": BuildExtension},
)
