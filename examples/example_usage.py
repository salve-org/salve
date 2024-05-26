from salve import IPC, Response
from selectors import EVENT_READ, DefaultSelector
from os import set_blocking
from sys import stdin, stdout


autocompleter = IPC()  # only_newest=True)

set_blocking(stdin.fileno(), False)
set_blocking(stdin.fileno(), False)
selector = DefaultSelector()
selector.register(stdin, EVENT_READ)

stdout.write("Code: \n")
stdout.flush()

while True:
    # Keep IPC alive
    autocompleter.ping()

    # Check input
    events = selector.select(0.025)
    if events:
        # Make requests
        for line in stdin:
            autocompleter.request(
                "autocomplete",
                expected_keywords=[],
                full_text=line,
                current_word=line[-2],
            )

    # Check output
    if not autocompleter.has_response():
        continue
    output: Response | None = autocompleter.get_response()
    stdout.write(str(output) + "\n")
    stdout.flush()
