import tkinter as tk
from tkinter import ttk
import time
import webview



def open_browser():
    # Wait for Flask server to start
    time.sleep(2)
    webview.create_window(title='Unfair Hangman', url="http://127.0.0.1:8888", height=700)
    webview.start()


# Create Tkinter window
tk = tk.Tk()
tk.title("Hangman - Web Game")

frame = ttk.Frame(tk, padding=20)
frame.grid()

open_browser()


tk.mainloop()
