"""Small desktop demo (Tkinter) that uses the local core API to list/create items."""
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox

API_BASE = "http://127.0.0.1:5000/api/v1"


def list_items():
    r = requests.get(f"{API_BASE}/items")
    if r.status_code != 200:
        messagebox.showerror("Error", "Cannot fetch items")
        return []
    return r.json()


def create_item(title, content):
    r = requests.post(f"{API_BASE}/items", json={"title": title, "content": content})
    return r.status_code == 200


def refresh_list(lb):
    lb.delete(0, tk.END)
    items = list_items()
    for it in items:
        lb.insert(tk.END, f"{it['id'][:8]} {it['title']}")


def main():
    root = tk.Tk()
    root.title("DeadInside Demo")

    lb = tk.Listbox(root, width=80, height=20)
    lb.pack()

    frm = tk.Frame(root)
    frm.pack()

    def on_add():
        title = simpledialog.askstring("Title", "Enter title:")
        if not title:
            return
        create_item(title, "")
        refresh_list(lb)

    tk.Button(frm, text="Refresh", command=lambda: refresh_list(lb)).pack(side=tk.LEFT)
    tk.Button(frm, text="Add", command=on_add).pack(side=tk.LEFT)

    refresh_list(lb)
    root.mainloop()


if __name__ == '__main__':
    main()
