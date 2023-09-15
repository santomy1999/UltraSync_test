import asyncio
import websockets

async def receive_and_display_coordinates():
    uri = "ws://SERVER_IP:8765"  # Replace SERVER_IP with the server's IP address or domain name
    async with websockets.connect(uri) as websocket:
        while True:
            coordinates = await websocket.recv()
            print(coordinates)

asyncio.get_event_loop().run_until_complete(receive_and_display_coordinates())
