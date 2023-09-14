# Importing the relevant libraries
import websockets
import asyncio
import tkinter as tk
import pyautogui
import threading

# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Calculate the scaling factors for coordinates
SCALE_FACTOR = 2/3

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH *SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))

URL = "ws://192.168.1.13:7890"

CLIENT1_OBJECT_NAME = "white"
CLIENT2_OBJECT_NAME = "blue"

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
    # Initial coordinates
    x_coordinate = int(SCREEN_WIDTH / 2)  # Start in the center of the screen
    y_coordinate = int(SCREEN_HEIGHT / 2)

    # Place the initial object
    # place_object(x_coordinate, y_coordinate,CLIENT_OBJECT_NAME)
    # place_object(x_coordinate,y_coordinate,"blue")

    # Start the tkinter main loop
    window.mainloop()




def place_object(x, y,object_name):
    canvas.delete(object_name)  # Clear any existing objects
    x=x*SCALE_FACTOR
    y=y*SCALE_FACTOR
    canvas.create_rectangle(x, y, x + 15, y + 15, fill=object_name, tags=object_name)
   
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
        update_coordinates(x,y,CLIENT1_OBJECT_NAME)
        # time.sleep(100/1000)
        

# Function to capture and return mouse pointer data
def capture_mouse_data():
    x, y = pyautogui.position()
    return x, y

# Function to send mouse pointer data to the server
async def send_mouse_data():
    # url = "ws://192.168.1.13:7890"  # Replace with your server URL
    async with websockets.connect(URL) as ws:
        while True:
            x, y = capture_mouse_data()
            message = f"c2:x={x+10},y={y+10}"
            await ws.send(message)
            await asyncio.sleep(0.1)  # Adjust the delay as needed


# The main function that will handle connection and communication 
# with the server
async def listen():
    # url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(URL) as ws:
        # Send a greeting message
        while True:
            msg = await ws.recv()
            cli,msg=msg.split(":")
            if cli=="c1":
                display_object(msg,CLIENT2_OBJECT_NAME)
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

# # Start client object display in a seperate thread
# object_display_thread = threading.Thread(target=display_client_object)
# object_display_thread.daemon = True
# object_display_thread.start()

# Wait for both threads to finish
websocket_thread.join()
tkinter_thread.join()
# object_display_thread.join()
# asyncio.get_event_loop().run_until_complete(listen())
