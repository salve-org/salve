# pip uninstall salve_ipc -y --break-system-packages; pip install . --break-system-packages --no-build-isolation
from setuptools import setup

with open("README.md", "r") as file:
    long_description = file.read()


setup(
    name="salve_ipc",
    version="0.3.1",
    description="A module that makes easily provides autocompletions, replacement suggestions, and syntax highlighting to your code editor",
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
