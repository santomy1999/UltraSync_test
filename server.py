import asyncio
import websockets
import pyautogui

# Store connected clients
connected_clients = set()

async def send_mouse_coordinates(websocket, path):
    connected_clients.add(websocket)
    
    try:
        while True:
            x, y = pyautogui.position()
            coordinates = f"x={x},y={y}"
            await asyncio.gather(
                *[client.send(coordinates) for client in connected_clients]
            )
            await asyncio.sleep(.0001)  # Adjust the delay as needed
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.remove(websocket)

start_server = websockets.serve(send_mouse_coordinates, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
