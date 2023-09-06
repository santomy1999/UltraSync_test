import tkinter as tk
import asyncio
import websockets
import threading
import pyautogui  # Used to get screen dimensions

# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH / 3) * 2)
WINDOW_HEIGHT = int((SCREEN_HEIGHT / 3) * 2)

# Calculate the scaling factors for coordinates
X_SCALE_FACTOR = SCREEN_WIDTH / WINDOW_WIDTH
Y_SCALE_FACTOR = SCREEN_HEIGHT / WINDOW_HEIGHT

def place_object(x, y):
    canvas.delete("object")  # Clear any existing objects
    canvas.create_rectangle(x, y, x + 5, y + 5, fill="blue", tags="object")

def trace_coordinates(x, y, prev_x, prev_y):
    canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)

def update_coordinates(x_coordinate, y_coordinate, prev_x, prev_y):
    place_object(x_coordinate, y_coordinate)
    trace_coordinates(x_coordinate, y_coordinate, prev_x, prev_y)

async def receive_and_display_coordinates():
    uri = "ws://192.168.1.5:8765"  # Replace SERVER_IP with the server's IP address or domain name
    async with websockets.connect(uri) as websocket:
        prev_x, prev_y = None, None  # Initialize previous coordinates
        while True:
            coordinates = await websocket.recv()
            parts = coordinates.split(',')

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
            
            if x_coordinate is not None and y_coordinate is not None:
                # Scale the coordinates to match the screen size
                x_coordinate = int(x_coordinate / X_SCALE_FACTOR)
                y_coordinate = int(y_coordinate / Y_SCALE_FACTOR)
                if prev_x is not None and prev_y is not None:
                    update_coordinates(x_coordinate, y_coordinate, prev_x, prev_y)
                prev_x, prev_y = x_coordinate, y_coordinate

def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(receive_and_display_coordinates())

# Create the Tkinter window with the specified dimensions
window = tk.Tk()
window.title("Object Placement")
window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Create a canvas to draw on
canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
canvas.pack()

# Initial coordinates
x_coordinate = int(SCREEN_WIDTH / 2)  # Start in the center of the screen
y_coordinate = int(SCREEN_HEIGHT / 2)

# Place the initial object
place_object(x_coordinate, y_coordinate)

# Start the WebSocket communication thread
websocket_thread = threading.Thread(target=start_websocket_thread)
websocket_thread.daemon = True
websocket_thread.start()

# Start the Tkinter main loop
window.mainloop()
