# Importing the relevant libraries
import websockets
import asyncio
import tkinter as tk
import pyautogui
import threading
from PIL import ImageTk, Image
import tkinter.font as tkFont

# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Calculate the scaling factors for coordinates
SCALE_FACTOR = 2/3

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH *SCALE_FACTOR))
WINDOW_HEIGHT = int((SCREEN_HEIGHT * SCALE_FACTOR))

URL = "ws://192.168.0.188:7890"

canvas = None

doctor  ={"name":   "Doctor's Probe"    , "color":   "#9da6fc",    "label":   None,
          "image":   "doctor.png",   "imageInstance":    None,   "canvasId": None,  "x" : None ,    "y" :   None}
lab     ={"name":   "Lab's Probe"       , "color":   "#8cedc1",   "label":   None,
          "image":   "lab.png",      "imageInstance":    None,   "canvasId": None,  "x" : None ,    "y" :   None}
synclabel = None
bg = "graph-background.jpg"
# Function to initialize and run the tkinter GUI
def run_tkinter():
    global canvas
    global synclabel
    # Create the Tkinter window with the specified dimensions
    window = tk.Tk()
    window.title("Lab")



    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a canvas to draw on
    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    # background image
    bgimage = ImageTk.PhotoImage(file = bg)
    canvas.create_image(10, 10, image = bgimage, anchor = tk.NW)

    
    synclabel =create_label(window, "Not in sync")
    synclabel.place(x=430,y=40,width=180,height=40)
    synclabel.configure(bg="white")
    # creating label for both clients

    lab["label"] = create_label(window, lab["name"])
    doctor["label"] = create_label(window, f"{doctor['name']}: Not Connected")



    doctor["label"].place(x=30,y=40,width=180,height=40)
    lab["label"].place(x=220,y=40,width=180,height=40)

    doctor["label"].configure(bg=doctor["color"])
    lab["label"].configure(bg=lab["color"])

    image1 =  Image.open(doctor["image"])
    doctor["imageInstance"] = ImageTk.PhotoImage(image1)

    image2 =  Image.open(lab["image"])
    lab["imageInstance"] = ImageTk.PhotoImage(image2)
    
    # Place the initial object
    # place_object(x_coordinate, y_coordinate,CLIENT_OBJECT_NAME)
    # place_object(x_coordinate,y_coordinate,"blue")

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
    if lab["x"]==doctor["x"]:
        synclabel.config(text=f"Synced") 
    else:
        synclabel.config(text=f"Not Synced")
# def trace_coordinates(x, y, prev_x, prev_y):
    # canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)

# Function to update object coordinates on the canvas
def update_coordinates(x_coordinate, y_coordinate,object):
    place_object(x_coordinate, y_coordinate,object)
    object["label"].config(text=f"{object['name']}:X: {x_coordinate}, Y: {y_coordinate}")   


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

def display_object(data,object):
    object["x"],object["y"]=extract_coordinates(data)
    update_coordinates(object["x"],object["y"],object)

def display_client_object():
        lab["x"],lab["y"]= pyautogui.position()
        update_coordinates(lab["x"],lab["y"],lab)
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
            message = f"c2:x={x},y={y}"
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
                display_object(msg,doctor)
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
# object_display_thread.join()
# asyncio.get_event_loop().run_until_complete(listen())
