import os
import re
import subprocess
import glob
import setuptools
from distutils.command.build_py import build_py as build_py_orig

class BuildProto(setuptools.Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        proto_files = glob.glob('carta-protobuf/*/*.proto')
        proto_dirs = set(os.path.dirname(f) for f in proto_files)
        includes = [f"-I{d}" for d in proto_dirs]
        subprocess.run([
            'protoc',
            *includes,
            '--python_out=cartaicdproto/',
            *proto_files,
        ])
        
        with open('cartaicdproto/__init__.py', 'w') as initfile:
            for pb2_file in glob.glob('cartaicdproto/*_pb2.py'):
                # There seriously isn't a better way to fix this relative import as of time of writing
                with open(pb2_file) as f:
                    data = f.read()
                data = re.sub("^(import .*_pb2)", r"from . \1", data, flags=re.MULTILINE)
                with open(pb2_file, 'w') as f:
                    f.write(data)
                    
                # We also automatically import all the submodules to allow discovery    
                submodule = os.path.splitext(os.path.basename(pb2_file))[0]
                initfile.write(f"from . import {submodule} as {submodule[:-4]}\n")
        
        # This is a horrible hack; it may be fixed in the latest protoc
        with open('cartaicdproto/enums_pb2.py') as f:
            data = f.read()
        data = re.sub("^None = 0$", "globals()['None'] = 0", data, flags=re.MULTILINE)
        with open('cartaicdproto/enums_pb2.py', 'w') as f:
            f.write(data)
        
class BuildPy (build_py_orig):
    def run(self):
        self.run_command('build_proto')
        super(BuildPy, self).run()

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cartaicd",
    version="0.0.1",
    author="Adrianna Pińska",
    author_email="adrianna.pinska@gmail.com",
    description="Python interface to the CARTA backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/idia-astro/carta-python-icd",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "websockets>=8.1",
    ],
    cmdclass={
        "build_py": BuildPy,
        "build_proto": BuildProto,
    },
)
