"""
    Edit history
    Author : yda
    Date : 2020-11-12

    Package name changed - asammdf to mdfstudio
"""

import sys
from cx_Freeze import setup, Executable
import shutil
import os

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "numpy", "pyqtgraph"],
    "excludes": [
        "gtk",
        "tkinter",
        "bcolz",
        "bokeh",
        "bs4",
        "alabaster",
        "babel",
        "cloudpickle",
        "blosc",
        "colorama",
        "cryptography",
        "Cython",
        "dask",
        "IPython",
        "jedi",
        "jinja2",
        "Levenshtein",
        "lxml",
        "netCDF4",
        "nose",
        "openpyxl",
        "PIL",
        "statsmodels",
        "tables",
        "sphinx",
        "sphinx_rtd_theme",
        "sqlalchemy",
        "tornado",
        "zmq",
        "botocore",
        "notebook",
        "cvxopt",
        "bottleneck",
        "cyordereddict",
        "cytoolz",
        "markupsafe",
        "psutil",
        "simplejson",
        "boto3",
        "docutils",
        "html5lib",
        "ipykernel",
        "ipyparallel",
        "ipython_genutils",
        "ipywidgets",
        "jmespath",
        "joblib",
        "jupyter_client",
        "jupyter_core",
        "mock",
        "msgpack",
        "pbr",
        "pkg_resources",
        "py",
        "pycparser",
        "s3fs",
        "s3transfer",
        "seaborn",
        "sortedcontainers",
        "tblib",
        "test",
        "toolz",
        "traitlets",
        "xarray",
        "xlrd",
        "zict",
    ],
}
# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

resource_path = os.path.join(
    os.getcwd(),
    "build",
    "exe.{}-{}.{}".format(sys.platform, sys.version_info[0], sys.version_info[1]),
    "lib",
    "mdfstudio",
)

build_path = os.path.join(
    os.getcwd(),
    "build",
    "exe.{}-{}.{}".format(sys.platform, sys.version_info[0], sys.version_info[1]),
)

setup(
    name="mdfstudio",
    version="3.4.1",
    description="GUI for mdfstudio",
    options={"build_exe": build_exe_options},
    executables=[Executable("mdfstudiogui.py", base=base, targetName="mdfstudio.exe")],
)

cwd = os.getcwd()

os.chdir(resource_path)
for item in os.listdir():
    print(item)
    if os.path.isdir(item):
        func = shutil.copytree
    else:
        func = shutil.copy

    func(item, os.path.join(build_path, item))
