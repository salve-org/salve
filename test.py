from time import sleep, time
from salve_ipc import IPC, Response
if __name__ == "__main__":

    context = IPC()
    sleep(1)

    context.update_file(
        "test",
        open(__file__, "r+").read(),
    )

    context.request(
        "autocomplete",
        file="test",
        expected_keywords=[],
        current_word="t",
    )

    st = time()
    while not (output := context.get_response("autocomplete")):
        continue
    print(output)  # type: ignore
    print(time()-st)
    context.kill_IPC()
