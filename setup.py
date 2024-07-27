# pip install -U -r requirements-dev.txt --break-system-packages; pip uninstall salve -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python3 -m pytest .
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="salve",
    version="1.1.0",
    description="Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, editorconfig suggestions, definitions, and syntax highlighting.",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/salve-org/salve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=open("requirements.txt", "r+")
    .read()
    .splitlines(keepends=False),
    python_requires=">=3.11",
    license="MIT license",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",  # I believe it can be classified as such, cannot test Windows
        "Programming Language :: Python :: Implementation",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    packages=[
        "salve",
        "salve.server_functions",
        "salve.server_functions.highlight",
    ],
)
