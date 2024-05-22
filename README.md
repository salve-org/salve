# Makeshift-LSP

This folder contains a makeshift LSP I am making for future code editors I make for myself so I don't have to recreate the highlighting and autocomplete code portions aevery time and it also allows me to narrow down my issues.

## Help wanted

I want to make this more of an RPC and that means using some IPC. Unfortunately, I have no idea how to make that happen. If someone is willing to help, I would appreciate no external dependencies (outside of the Python stdlib) and an example use case that fits the simple_server and simple_client example. I want to eventually make it such that the makeshift lsp is kept alive as a subprocess and incrementally changes files and updates its internal list of keywords so that highlighting can become more efficient by using tree-sitter and making the autocomplete more efficient by parsing less.

The following tangent explains my needs:

Imagine a tkinter app (non thread-safe) that allows someone to query a list and get the value at that index. Now, imagine the list is incredibly long. If it takes a while to get the item at the index in the below implementation, the app will lag. Now imagine that its syntax highlighting or autocomplete. That'll never do. What I want to do in this example is make the list holding functionality its own app/process that I can query (needs to be able to take input and respond with output (multiprocess.connections.Listener can't respond)) but it also keeps track of queries (stays alive past a single query) and then the main process updates once a value is returned via a callback. I want the app to run like normal (not be blocked/lagging) while it queries and if the user makes another query attempt while the one before is running the result is discarded in favor of the new request's output.

```python
from tkinter import Label, Tk, Entry, Event

app = Tk()

def get_info(_: Event):
    random_list = ["apples", "oranges", "bananas"]
    index = user_entry.get()
    user_entry.delete(0, "end")
    try:
        index = int(index)
    except ValueError:
        output_label.configure(
            text="Failed to get item"
        )
        return
    try:
        output_label.configure(
            text=f"Item at index {index}: {random_list[index]}"
        )
    except IndexError:
        output_label.configure(
            text="Failed to get item"
        )

user_entry = Entry(app)
user_entry.pack()
user_entry.bind("<Return>", get_info)
user_entry.focus()

output_label = Label(app, text="Item at index ?: ?")
output_label.pack()

app.mainloop()
```

Of course there are more sensible ways to solve the issue in this particular case but this is more an example to get my point and question across.
