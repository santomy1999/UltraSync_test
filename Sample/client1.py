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

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH * SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))


CLIENT_OBJECT_NAME = "green"


canvas = None
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
    # place_object(x_coordinate, y_coordinate)

    # Start the tkinter main loop
    window.mainloop()

def place_object(x, y,object_name):
    canvas.delete(object_name)  # Clear any existing objects
    x = x * SCALE_FACTOR
    y = y * SCALE_FACTOR
    canvas.create_rectangle(x, y, x + 5, y + 5, fill=object_name, tags=object_name)

# Function to update object coordinates on the canvas
def update_coordinates(x_coordinate, y_coordinate,object_name):
    place_object(x_coordinate, y_coordinate,object_name)

# Extract x, y coordinates from the websocket data
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

# Function to display object coordinates received from the server
def display_object(data,object_name):
    x, y = extract_coordinates(data)
    update_coordinates(x, y,object_name)

def display_client_object():
    x, y = pyautogui.position()
    update_coordinates(x+20,y+20,CLIENT_OBJECT_NAME)
    # time.sleep(100/1000)

# Function to capture and return mouse pointer data
def capture_mouse_data():
    x, y = pyautogui.position()
    return x, y

# The main function that will handle connection and communication 
# with the server to receive data
async def receive_coordinates():
    url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        # Receive and display coordinates from the server
        while True:
            msg = await ws.recv()
            display_object(msg,"blue")
            display_client_object()
            # x, y = extract_coordinates(msg)
            # place_object1(x+10,y+10)

# Start sending coordinates to the server
async def send_coordinates():
    url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(url) as ws:
        # Send coordinates to the server
        while True:
            x, y = capture_mouse_data()
            message = f"x={x},y={y}"
            await ws.send(message)
            # display_object(message,"blue")
            # display_client_object()
            # display_object(message)
            await asyncio.sleep(100/1000)


# Start the connection to receive data in a separate thread
def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_coordinates())

# Start sending coordinates in a separate thread
def start_send_coordinates_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_coordinates())


# Start the tkinter GUI in a separate thread
tkinter_thread = threading.Thread(target=run_tkinter)
tkinter_thread.daemon = True
tkinter_thread.start()

# Start the connection to send coordinates in a separate thread
websocket_thread = threading.Thread(target=start_websocket_thread)
websocket_thread.daemon = True
websocket_thread.start()

# Start the sending coordinates in a separate thread
send_coordinates_thread = threading.Thread(target=start_send_coordinates_thread)
send_coordinates_thread.daemon = True
send_coordinates_thread.start()


# Wait for all threads to finish
websocket_thread.join()
# send_coordinates_thread.join()
tkinter_thread.join()
