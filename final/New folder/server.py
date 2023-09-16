# Importing the relevant libraries
import websockets
import asyncio

PORT = 7890

print("Server listening on Port " + str(PORT))

# Maintain a set of connected clients
connected_clients = set()
disconnected_clients = set()  # New set to track disconnected clients

async def echo(websocket, path):
    connected_clients.add(websocket)
    print("A client just connected")
    try:
        while True:
            message = await websocket.recv()
            print("Received message from client: " + message)
            # Forward the message to all connected clients except the sender
            for client in connected_clients:
                if client != websocket:
                    await client.send(f"{message}")
                    # break
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
        disconnected_clients.add(websocket)
        connected_clients.remove(websocket)

# A background task to remove disconnected clients
async def remove_disconnected_clients():
    while True:
        for client in disconnected_clients.copy():
            if client in connected_clients:
                connected_clients.remove(client)
        disconnected_clients.clear()
        await asyncio.sleep(1)  # Adjust the delay as needed


start_server = websockets.serve(echo, "0.0.0.0", PORT)

# Start the background task to remove disconnected clients
asyncio.ensure_future(remove_disconnected_clients())

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
