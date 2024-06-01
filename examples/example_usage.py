from os import set_blocking
from selectors import EVENT_READ, DefaultSelector
from sys import stdin, stdout

from salve_ipc import IPC, Response

# Create context for IPC
context = IPC()

# Allow for nice input
set_blocking(stdin.fileno(), False)
set_blocking(stdin.fileno(), False)
selector = DefaultSelector()
selector.register(stdin, EVENT_READ)

# Print out "Code: "
stdout.write("Code: \n")
stdout.flush()

while True:
    # Keep IPC alive
    context.ping()

    # Check input
    events = selector.select(0.025)
    if events:
        # Make requests
        for line in stdin:
            # Update file
            context.update_file("test", line)

            # Make request to server
            context.request(
                "autocomplete",
                expected_keywords=[],
                file="test",
                current_word=line[-2],
            )

    # Check output
    # context.cancel_request("autocomplete") # Uncommenting this line will cause the request to always be cancelled
    output: Response | None = context.get_response("autocomplete")
    if not output:
        continue

    # Write response
    stdout.write(str(output) + "\n")
    stdout.flush()

context.kill_IPC()
