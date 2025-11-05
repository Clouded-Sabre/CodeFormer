#!/usr/bin/env python

from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDAExtension
import torch  # Import torch directly for CUDA check
import sys

def make_cuda_ext(name, module, sources, sources_cuda=None):
    if sources_cuda is None:
        sources_cuda = []
    define_macros = []
    extra_compile_args = {'cxx': []}
    if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
        define_macros += [('WITH_CUDA', None)]
        extension = CUDAExtension
        extra_compile_args['nvcc'] = [
            '-D__CUDA_NO_HALF_OPERATORS__',
            '-D__CUDA_NO_HALF_CONVERSIONS__',
            '-D__CUDA_NO_HALF2_OPERATORS__',
        ]
        sources += sources_cuda
    else:
        print(f'Compiling {name} without CUDA')
        extension = CppExtension
    return extension(
        name=f'{module}.{name}',
        sources=[os.path.join(*module.split('.'), p) for p in sources],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args)

if __name__ == '__main__':
    ext_modules = []
    if '--cuda_ext' in sys.argv:
        ext_modules = [
            make_cuda_ext(
                name='deform_conv_ext',
                module='ops.dcn',
                sources=['src/deform_conv_ext.cpp'],
                sources_cuda=['src/deform_conv_cuda.cpp', 'src/deform_conv_cuda_kernel.cu']),
            make_cuda_ext(
                name='fused_act_ext',
                module='ops.fused_act',
                sources=['src/fused_bias_act.cpp'],
                sources_cuda=['src/fused_bias_act_kernel.cu']),
            make_cuda_ext(
                name='upfirdn2d_ext',
                module='ops.upfirdn2d',
                sources=['src/upfirdn2d.cpp'],
                sources_cuda=['src/upfirdn2d_kernel.cu']),
        ]
        sys.argv.remove('--cuda_ext')

    setup(
        cmdclass={'build_ext': BuildExtension},
        ext_modules=ext_modules,
    )
