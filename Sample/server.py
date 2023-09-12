# Importing the relevant libraries
import websockets
import asyncio

PORT = 7890

print("Server listening on Port " + str(PORT))

# Maintain a set of connected clients
connected_clients = set()

async def echo(websocket, path):
    connected_clients.add(websocket)
    print("A client just connected")
    try:
        # async for message in websocket:
        while True:
            message = await websocket.recv()
            print("Received message from client: " + message)
            # Forward the message to all connected clients except the sender
            for client in connected_clients:
                if client != websocket:
                    await client.send(f"{message}")
                    await asyncio.sleep(100/1000)
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
        connected_clients.remove(websocket)

start_server = websockets.serve(echo, "0.0.0.0", PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
