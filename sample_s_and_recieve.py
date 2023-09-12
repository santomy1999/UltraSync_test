import websocket 
 
ws = websocket.WebSocket() 
ws.connect("ws://echo.websocket.org/") 
 
# Send a message to the WebSocket server 
ws.send("Hello, server!") 
 
# Receive a message from the WebSocket server 
message = ws.recv() 
print(message) # b'Hello, server!' 
 
ws.close() 