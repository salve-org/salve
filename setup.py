# pip install -r requirements.txt --break-system-packages; pip uninstall salve_ipc -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python3 -m pytest .
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="salve_ipc",
    version="0.6.0",
    description="Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, editorconfig suggestions, definitions, and syntax highlighting.",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/Moosems/salve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["pygments", "pyeditorconfig", "beartype"],
    python_requires=">=3.9",
    license="MIT license",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",  # I believe it can be classified as such, cannot test Windows
        "Programming Language :: Python :: Implementation",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    packages=["salve_ipc"],
)
