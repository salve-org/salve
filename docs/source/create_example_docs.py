from os import listdir, makedirs, path
from pathlib import Path
from shutil import rmtree

examples_dir = "./examples"
docs_examples_dir = "./docs/source/examples"

if Path(docs_examples_dir).exists():
    rmtree(docs_examples_dir)
makedirs(docs_examples_dir)

for filename in listdir(examples_dir):
    base_name = path.splitext(filename)[0]
    with open(
        path.join(docs_examples_dir, f"{base_name}.rst"), "w"
    ) as rst_file:
        rst_file.write(f'{"=" * len(base_name)}\n')
        new_name = ""
        split_name = base_name.split("_")
        for word in split_name:
            new_name += word.capitalize() + " "
        new_name = new_name[: len(new_name) - 1]
        rst_file.write(f"{new_name}\n")
        rst_file.write(f'{"=" * len(base_name)}\n\n')
        with open(path.join(examples_dir, filename), "r") as example_file:
            rst_file.write(".. code-block:: python\n\n")
            for line in example_file:
                rst_file.write(f"    {line}")
        rst_file.write(
            f"\nSee the file example file `here <{'https://github.com/salve-org/salve/blob/master/examples/' + filename}>`_."
        )
