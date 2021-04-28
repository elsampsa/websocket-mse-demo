# WS server example

import asyncio
import websockets
import time
import subprocess
import numpy

# dump mp4 to stdin

st="ffmpeg -r 5 -i rtsp://admin:12345@192.168.0.157 -c:v copy -an -movflags frag_keyframe+empty_moov -f mp4 pipe:1"
# .. if I create a file with the same command, it does work ok with html5 video element


async def hello(websocket, path):
    """This is only started upon connection
    
    So .. call ffmpeg process in a subprocess .. read the stdin
    it should give the initial packet ok
    
    """

    packetsize=512
    
    ps = subprocess.Popen(st.split(), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    cc=0
    while True:
        packet = ps.stdout.read(packetsize)
        """ # uncomment for extra verbosity
        a= numpy.frombuffer(packet, dtype=numpy.uint8)
        print("["+str(len(packet))+"]")
        print(a)
        print()
        """
        await websocket.send(packet)
        cc+=1
        #if (cc>=3000): # uncomment for debugging
        #    break
        

start_server = websockets.serve(hello, 'localhost', 3001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

