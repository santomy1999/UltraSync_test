import asyncio
import websockets
import pyautogui
import threading
import tkinter as tk


# Constants for the screen size
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Calculate the window dimensions to match the specified aspect ratio and 1/3 the total area
WINDOW_WIDTH = int((SCREEN_WIDTH / 3) * 2)
WINDOW_HEIGHT = int((SCREEN_HEIGHT / 3) * 2)

# Calculate the scaling factors for coordinates
X_SCALE_FACTOR = SCREEN_WIDTH / WINDOW_WIDTH
Y_SCALE_FACTOR = SCREEN_HEIGHT / WINDOW_HEIGHT


# Store connected clients
connected_clients = set()

# Create a global variable for the tkinter window
window = None

def update_coordinates(x, y):
    if window:
        canvas.delete("object")  # Clear any existing objects
        canvas.create_rectangle(x, y, x + 5, y + 5, fill="green", tags="object")

async def send_mouse_coordinates(websocket, path):
    connected_clients.add(websocket)
    
    try:
        while True:
            x, y = pyautogui.position()
            update_coordinates(x, y)
            coordinates = f"x={x},y={y}"
            await asyncio.gather(
                *[client.send(coordinates) for client in connected_clients]
            )
            await asyncio.sleep(0.01)  # Adjust the delay as needed
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

def start_websocket_server():
    asyncio.set_event_loop(asyncio.new_event_loop())  # Create a new event loop
    start_server = websockets.serve(send_mouse_coordinates, "0.0.0.0", 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def create_tkinter_window():
    global window
    window = tk.Tk()
    window.title("Object Placement")
    window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    global canvas
    canvas = tk.Canvas(window, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    canvas.pack()

    window.mainloop()

# Start the WebSocket server and the tkinter window in separate threads
tkinter_thread = threading.Thread(target=create_tkinter_window)
websocket_thread = threading.Thread(target=start_websocket_server)


websocket_thread.start()
tkinter_thread.start()
