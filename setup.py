#!/usr/bin/env python3

import multiprocessing
import os
import subprocess
import sys

import setuptools
from setuptools.command.install import install
from sphinx.setup_command import BuildDoc
from wheel.bdist_wheel import bdist_wheel

VERSION = (0, 5, 2)


def version_str(version):
    return ".".join(map(str, version))


class platform_bdist_wheel(bdist_wheel):
    """Patched bdist_well to make sure wheels include platform tag."""

    def finalize_options(self):
        bdist_wheel.finalize_options(self)
        self.root_is_pure = False

class InstallPlatlib(install):
    def finalize_options(self):
        install.finalize_options(self)
        self.install_lib = self.install_platlib


def configure_c_extension():
    """Configure cmake project to C extension."""
    print(
        f"Configuring for python {sys.version_info.major}.{sys.version_info.minor}..."
    )
    os.makedirs("cmake_build", exist_ok=True)
    cmake_command = [
        "cmake",
        "../opensfm/src",
        "-DPYTHON_EXECUTABLE=" + sys.executable,
    ]
    if sys.platform == "win32":
        cmake_command += [
            "-DVCPKG_TARGET_TRIPLET=x64-windows",
            "-DCMAKE_TOOLCHAIN_FILE=../vcpkg/scripts/buildsystems/vcpkg.cmake",
        ]
    subprocess.check_call(cmake_command, cwd="cmake_build")


def build_c_extension():
    """Compile C extension."""
    print("Compiling extension...")
    if sys.platform == "win32":
        subprocess.check_call(
            ["cmake", "--build", ".", "--config", "Release"], cwd="cmake_build"
        )
    else:
        subprocess.check_call(
            ["make", "-j" + str(multiprocessing.cpu_count())], cwd="cmake_build"
        )


configure_c_extension()
build_c_extension()

install_requires = []
with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="opensfm",
    version=version_str(VERSION),
    description="A Structure from Motion library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mapillary/OpenSfM",
    project_urls={
        "Documentation": "https://docs.opensfm.org/",
    },
    author="Mapillary",
    license="BSD",
    packages=setuptools.find_packages(),
    scripts=[
        "bin/import_colmap.py",
        "bin/opensfm.bat",
        "bin/plot_features",
        "bin/plot_tracks",
        "bin/create_calibrtion_pattern",
        "bin/import_video",
        "bin/opensfm_main.py",
        "bin/plot_gcp.py",
        "bin/run_bundler",
        "bin/export_geojson",
        "bin/iterative_self_calibration",
        "bin/opensfm_run_all",
        "bin/plot_inliers",
        "bin/update_geotag",
        "bin/export_gps",
        "bin/migrate_undistort.sh",
        "bin/opensfm_run_all.bat",
        "bin/plot_matches.py",
        "bin/import_bundler",
        "bin/opensfm",
        "bin/plot_depthmaps",
        "bin/plot_submodels_gps",
    ],
    package_data={
        "opensfm": [
            "pybundle.*",
            "pygeo.*",
            "pygeometry.*",
            "pyrobust.*",
            "pyfeatures.*",
            "pydense.*",
            "pysfm.*",
            "pyfoundation.*",
            "pymap.*",
            "data/sensor_data.json",
            "data/camera_calibration.yaml",
            "data/bow/bow_hahog_root_uchar_10000.npz",
            "data/bow/bow_hahog_root_uchar_64.npz",
        ]
    },
    cmdclass={
        "bdist_wheel": platform_bdist_wheel,
        "build_doc": BuildDoc,
        "install": InstallPlatlib,
    },
    command_options={
        "build_doc": {
            "project": ("setup.py", "OpenSfM"),
            "version": ("setup.py", version_str(VERSION[:2])),
            "release": ("setup.py", version_str(VERSION)),
            "source_dir": ("setup.py", "doc/source"),
            "build_dir": ("setup.py", "build/doc"),
        }
    },
    install_requires=install_requires
)

