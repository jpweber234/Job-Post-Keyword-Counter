from datacollection import *

# Creates run button
run_button = ttk.Button(text="Run", width=20, command=run)
run_button.grid(row=6, column=0, padx=10, pady=10)

# Executes Tkinter loop to display GUI
root.mainloop()
