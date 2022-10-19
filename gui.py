from tkinter import *
from tkinter import filedialog

def browse():
    dir = filedialog.askopenfilename(initialdir="",title="Browse")
    return dir

window = Tk()
button = Button(text="Open File", command=browse)
button.pack()


window.mainloop()  
