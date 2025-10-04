import tkinter as tk

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Uber Driver Assistant")
        self.window.geometry("400x300")

        def handle_button_press():
            self.window.destroy()

        button = tk.Button(self.window, text="Close", command=handle_button_press)
        button.pack()

        # Start the event loop.
        self.window.mainloop()