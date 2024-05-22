from tkinter import Label, Tk, Entry, Event
from simple_server import get_item

app = Tk()


def interface_server(_: Event) -> None:
    item_at_index = get_item(user_entry.get())
    if item_at_index == "?":
        output_label.configure(text="Item could not be retrieved at index")
        return

    output_label.configure(text=f"Item index: {item_at_index}")


user_entry = Entry(app)
user_entry.pack()
user_entry.bind("<Return>", interface_server)
user_entry.focus()

output_label = Label(app, text="Item at index ?: ?")
output_label.pack()

app.mainloop()
