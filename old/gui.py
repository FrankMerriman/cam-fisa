from tkinter import *
from tkinter import ttk
# from tkvideo import tkvideo
root = Tk()
root.geometry("320x240")
frm = ttk.Frame(root, padding=5)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=1)
root.mainloop()