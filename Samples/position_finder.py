import tkinter as tk
import pyautogui

def update_coordinates():
    x, y = pyautogui.position()
    coordinates_label.config(text=f"X: {x}, Y: {y}")
    root.after(100, update_coordinates)

root = tk.Tk()
root.title("Mouse Pointer Coordinates")

coordinates_label = tk.Label(root, text="", font=("Arial", 16))
coordinates_label.pack(pady=20)

update_coordinates()

root.mainloop()
