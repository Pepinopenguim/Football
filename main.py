import random as rdm
import tkinter as tk
from tkinter import ttk, PhotoImage
import ttkthemes

import os



class Match(tk.Tk):
    def __init__(self, homeclub, awayclub, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.homeclub, self.awayclub = homeclub, awayclub

        self.minsize(400,400)

        self.setup_gui()
        
        self.setup_styler()

    def setup_styler(self):
        self.styler = ttkthemes.ThemedStyle()
        self.styler.theme_use("itft1")

    def setup_gui(self):
        self.mainframe = ttk.Frame(self)
        self.mainframe.pack(fill="both", expand=True)
        ttk.Button(self.mainframe, text="Test").pack(fill="x", padx=5, pady=5)

        self.load_image_onto_frame(self.mainframe, "images\\Bahia.svg", padx=5, pady=5)



    def load_image_onto_frame(self, frame, file, **pack_kwargs):
        image = PhotoImage(file=file)

        image_label = tk.Label(frame, image)
        image_label.pack(**pack_kwargs)



if __name__ == "__main__":

    app = Match(None, None)
    app.mainloop()