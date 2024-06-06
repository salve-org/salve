# pip uninstall salve_ipc -y --break-system-packages; pip install . --break-system-packages --no-build-isolation; python tests/test_ipc.py
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="salve_ipc",
    version="0.3.3",
    description="Salve is an IPC library that can be used by code editors to easily get autocompletions, replacements, and syntax highlighting.",
    author="Moosems",
    author_email="moosems.j@gmail.com",
    url="https://github.com/Moosems/salve",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["pygments"],
    python_requires=">=3.9",
    license="MIT license",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    packages=["salve_ipc"],
    package_data={
        "salve_ipc": ["./*", "./highlight/*"],
        "./": ["requirements.txt"],
    },
)
