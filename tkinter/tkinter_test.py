from tkinter import *
from tkinter import ttk

root = Tk()
root.geometry("200x220")
frame = Frame(root)
frame.pack()
 
label = Label(root,text = "A list of Grocery items.")
label.pack()

items = ["Bread", "Milk"]
list_items = StringVar(value=items)
listbox = Listbox(root, listvariable=list_items)


listbox.pack()
root.mainloop()
print(listbox.curselection())