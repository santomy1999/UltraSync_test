# Importing the relevant libraries
import websockets
import asyncio
import pyautogui
import tkinter as tk
import threading
# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


# Calculate the scaling factors for coordinates
SCALE_FACTOR = 2/3
# SCREEN_WIDTH / WINDOW_WIDTH
# Y_SCALE_FACTOR = SCREEN_HEIGHT / WINDOW_HEIGHT

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH *SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))


# Function to initialize and run the tkinter GUI
def run_tkinter():
    global canvas

    # Create the Tkinter window with the specified dimensions
    window = tk.Tk()
    window.title("Client One")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a canvas to draw on
    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    # Initial coordinates
    x_coordinate = int(SCREEN_WIDTH / 2)  # Start in the center of the screen
    y_coordinate = int(SCREEN_HEIGHT / 2)

    # Place the initial object
    place_object(x_coordinate, y_coordinate)

    # Start the tkinter main loop
    window.mainloop()

def place_object(x, y):
    canvas.delete("object")  # Clear any existing objects
    x=x*SCALE_FACTOR
    y=y*SCALE_FACTOR
    canvas.create_rectangle(x, y, x + 5, y + 5, fill="blue", tags="object")

# def trace_coordinates(x, y, prev_x, prev_y):
    # canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)

def update_coordinates(x_coordinate, y_coordinate):
    place_object(x_coordinate, y_coordinate)
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

def display_object(data):
    x,y=extract_coordinates(data)
    update_coordinates(x,y)

def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_coordinates())


# The main function that will handle connection and communication 
# with the server
async def send_coordinates():
    url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        # Send coordinates to the server
        while True:
            x, y = pyautogui.position()
            message = f"x={x},y={y}"
            await ws.send(message)
            display_object(message)
            await asyncio.sleep(100/1000)

# Start sending coordinates
# asyncio.get_event_loop().run_until_complete(send_coordinates())

# Start the connection in a separate thread
websocket_thread = threading.Thread(target=start_websocket_thread)
websocket_thread.daemon = True
websocket_thread.start()

# Start the tkinter GUI in a separate thread
tkinter_thread = threading.Thread(target=run_tkinter)
tkinter_thread.daemon = True
tkinter_thread.start()

# Wait for both threads to finish
websocket_thread.join()
tkinter_thread.join()