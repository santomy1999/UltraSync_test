# Importing the relevant libraries
import websockets
import asyncio
import pyautogui
import tkinter as tk
import threading
from PIL import ImageTk, Image
import tkinter.font as tkFont
# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Calculate the scaling factors for coordinates
SCALE_FACTOR = 2/3

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH * SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))

URL = "ws://192.168.125.162:7890"

canvas = None
# my_label = None
# his_label = None

doctor  ={"name":   "Doctor's Probe"    , "color":   "#9da6fc",    "label":   None,
          "image":   "doctor.png",   "imageInstance":    None,   "canvasId": None}
lab     ={"name":   "Lab's Probe"       , "color":   "#8cedc1",   "label":   None,
          "image":   "lab.png",      "imageInstance":    None,   "canvasId": None}



bg = "graph-background.jpg"
# background_image = Image.open("graph_background.jpg")
# background_photo = ImageTk.PhotoImage(background_image)

# Function to initialize and run the tkinter GUI
def run_tkinter():
    global canvas
    # global my_label
    # Create the Tkinter window with the specified dimensions
    window = tk.Tk()
    window.title("Doctor")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a canvas to draw on
    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    # background image
    bgimage = ImageTk.PhotoImage(file = bg)
    canvas.create_image(10, 10, image = bgimage, anchor = tk.NW)
    
    # creating label for both clients

    doctor["label"] = create_label(window, doctor["name"])
    lab["label"] = create_label(window, f"{lab['name']}: Not Connected")



    doctor["label"].place(x=30,y=40,width=180,height=40)
    lab["label"].place(x=220,y=40,width=180,height=40)

    doctor["label"].configure(bg=doctor["color"])
    lab["label"].configure(bg=lab["color"])

    image1 =  Image.open(doctor["image"])
    doctor["imageInstance"] = ImageTk.PhotoImage(image1)

    image2 =  Image.open(lab["image"])
    lab["imageInstance"] = ImageTk.PhotoImage(image2)
    
    # Start the tkinter main loop
    window.mainloop()


# Function to create and configure a label widget
def create_label(parent, text):
    label = tk.Label(parent)
    ft = tkFont.Font(family='Times', size=10)
    label["font"] = ft
    label["fg"] = "#333333"
    label["justify"] = "center"
    label["text"] = text
 
    # canvas.create_rectangle(10,40, 20, 50, fill=doctor["color"], tags="label c1")
    # canvas.create_rectangle(20,40, 30, 50, fill=lab["color"], tags="label c2")
    return label

def place_object(x, y,object):
    canvas.delete(object["canvasId"])  # Clear any existing objects
    x = x * SCALE_FACTOR
    y = y * SCALE_FACTOR
    # canvas.create_rectangle(x, y, x + 10, y + 10, fill=object["color"], tags=object["name"])
    object["canvasId"] = canvas.create_image(x, y, anchor=tk.NW, image=object["imageInstance"])
# Function to update object coordinates on the canvas
def update_coordinates(x_coordinate, y_coordinate,object):
    place_object(x_coordinate, y_coordinate,object)
    object["label"].config(text=f"{object['name']}:X: {x_coordinate}, Y: {y_coordinate}")   
    # Update the my_label text with the new coordinates
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
    global doctor
    x, y = pyautogui.position()
    update_coordinates(x,y,doctor)
    # time.sleep(100/1000)

# Function to capture and return mouse pointer data
def capture_mouse_data():
    x, y = pyautogui.position()
    return x, y

# The main function that will handle connection and communication 
# with the server to receive data
async def receive_coordinates():
    # url = "ws://192.168.1.13:7890"
    # Connect to the server
    global lab
    global doctor
    async with websockets.connect(URL) as ws:
        # Receive and display coordinates from the server
        while True:
            msg = await ws.recv()
            cli,msg=msg.split(":")
            if cli=="c2":
                display_object(msg,lab)
            display_client_object()
            # x, y = extract_coordinates(msg)
            # place_object1(x+10,y+10)

# Start sending coordinates to the server
async def send_coordinates():
    # url = "ws://192.168.1.13:7890"
    # Connect to the server
    async with websockets.connect(URL) as ws:
        # Send coordinates to the server
        while True:
            x, y = capture_mouse_data()
            message = f"c1:x={x},y={y}"
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
