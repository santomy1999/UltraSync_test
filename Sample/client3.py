# Importing the relevant libraries
import websockets
import asyncio
# import tkinter
import tkinter as tk
import pyautogui
import threading
import time
from PIL import Image, ImageTk  # Import Pillow

# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


# Calculate the scaling factors for coordinates
SCALE_FACTOR = 2/3

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH *SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))

CLIENT_OBJECT_NAME = "green"

canvas = None
# Function to initialize and run the tkinter GUI
def run_tkinter():
    
    global canvas
    # Create the Tkinter window with the specified dimensions
    window = tk.Tk()
    window.title("Client 2")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a canvas to draw on
    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    # Start the tkinter main loop
    window.mainloop()




def place_object(x, y,object_name):
    canvas.delete(object_name)  # Clear any existing objects
    x=x*SCALE_FACTOR
    y=y*SCALE_FACTOR
    canvas.create_rectangle(x, y, x + 5, y + 5, fill=object_name, tags=object_name)

# def trace_coordinates(x, y, prev_x, prev_y):
    # canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)

def update_coordinates(x_coordinate, y_coordinate,object_name):
    place_object(x_coordinate, y_coordinate,object_name)
    # trace_coordinates(x_coordinate, y_coordinate, prev_x, prev_y)

#Extract x,y coordinates from the websocket data
def extract_coordinates(data):
    parts = data.split(',')

    # Initialize variables
    x_coordinate = None
    y_coordinate = None

    # Iterate through the parts to extract the coordinates
    for part in parts:
        key, value = part.split('=')
        if key == 'x':
            x_coordinate = int(value)
        elif key == 'y':
            y_coordinate = int(value)
        

    return x_coordinate, y_coordinate

def display_object(data,object_name):
    x,y=extract_coordinates(data)
    update_coordinates(x,y,object_name)

def display_client_object():
        x, y = pyautogui.position()
        update_coordinates(x+20,y+20,CLIENT_OBJECT_NAME)
        # time.sleep(100/1000)
        

# Function to capture and return mouse pointer data
def capture_mouse_data():
    x, y = pyautogui.position()
    return x, y

# Function to send mouse pointer data to the server
async def send_mouse_data():
    url = "ws://192.168.1.9:7890"  # Replace with your server URL
    async with websockets.connect(url) as ws:
        while True:
            x, y = capture_mouse_data()
            message = f"x={x},y={y}"
            await ws.send(message)
            await asyncio.sleep(0.1)  # Adjust the delay as needed


# The main function that will handle connection and communication 
# with the server
async def listen():
    url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        # Send a greeting message
        while True:
            msg = await ws.recv()
            # await asyncio.sleep(0.01)
            display_object(msg,"blue")
            display_client_object()
            
            # print(msg)
# Start sending coordinates in a separate thread
def start_send_coordinates_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_mouse_data())

def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen())

# Start the tkinter GUI in a separate thread
tkinter_thread = threading.Thread(target=run_tkinter)
tkinter_thread.daemon = True
tkinter_thread.start()

# Start the connection in a separate thread
websocket_thread = threading.Thread(target=start_websocket_thread)
websocket_thread.daemon = True
websocket_thread.start()


# Start sending mouse data in a separate thread
mouse_data_thread = threading.Thread(target=start_send_coordinates_thread)
mouse_data_thread.daemon = True
mouse_data_thread.start()


# Wait for both threads to finish
websocket_thread.join()
tkinter_thread.join()
