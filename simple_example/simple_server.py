from json import dumps, loads
from os import set_blocking
from sys import exit, stdin, stdout
from time import sleep, time
from resreq import ResReq

random_list: list[str] = ["apples", "oranges", "bananas"]


def get_item(index: str) -> str:
    try:
        intdex = int(index)
    except ValueError:
        return "?"

    try:
        return random_list[intdex]
    except IndexError:
        return "?"


id_list: list[int] = []
newest_request: ResReq | None = None
newest_id: int = 0
old_time: float = time()
set_blocking(stdin.fileno(), False)
set_blocking(stdout.fileno(), False)
while True:
    current_time = time()
    if current_time - old_time > 5:
        exit(0)

    for line in stdin:
        old_time = current_time
        json_input: ResReq = loads(line)
        id: int = json_input["id"]
        if json_input["type"] == "refresh":
            stdout.write(
                dumps(
                    {
                        "id": id,
                        "type": "response",
                    }
                )
                + "\n"
            )
            stdout.flush()
            continue
        id_list.append(id)
        newest_id = id
        newest_request = json_input

    for id in id_list:
        if id == newest_id:
            continue
        stdout.write(dumps({"id": id, "type": "cancelled"}) + "\n")

    if not newest_request:
        continue

    index_request: str = newest_request["index"]  # type: ignore
    item = get_item(index_request)

    stdout.write(dumps({"id": newest_id, "type": "response", "item": item}) + "\n")
    stdout.flush()

    id_list = []
    newest_request = None
    newest_id = 0
    sleep(0.025)
