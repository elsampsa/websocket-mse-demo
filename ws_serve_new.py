import time, os, sys, shlex, subprocess
import asyncio, websockets
from valkka.core import *
from valkka.api2 import FragMP4ShmemClient

rtsp_adr = sys.argv[1]

"""Start nginx reverse proxy as a subprocess
"""
inipath = "./nginx.conf"
# nginx -p /tmp -c nginx.conf -g 'error_log error.log;'
comm = "nginx -p %s -c %s -g 'error_log error.log;'" % (".", inipath)
print("starting nginx with>", comm)
nginx_process = subprocess.Popen(shlex.split(comm))
# sys.exit(2) # debug

"""libValkka part.  Based on: https://elsampsa.github.io/valkka-examples/_build/html/lesson_4.html#receiving-frag-mp4-at-python

The filtergraph for simultaneous video viewing and frag-MP4 muxing looks like this:

::

                                                               
  (LiveThread:livethread) -->----------------------------------+  main branch (forks into two)
                                                               |   
  (OpenGLThread:glthread) <----(AVThread:avthread) << ---------+  decoding branch
                                                               |
       +-----------------------------------------<-------------+  mux branch
       |
       +--> {FragMP4MuxFrameFilter:fragmp4muxer} --> {FragMP4ShmemFrameFilter:fragmp4shmem}         
        
"""

shmem_buffers = 10 # 10 element in the ring-buffer
shmem_name = "lesson_4_c" # unique name identifying the shared memory
cellsize = 1024*1024*3 # max size for each MP4 fragment
timeout = 1000 # in ms

# decoding branch
glthread        =OpenGLThread("glthread")
gl_in_filter    =glthread.getFrameFilter()
avthread        =AVThread("avthread",gl_in_filter)
av_in_filter    =avthread.getFrameFilter()

# mux branch
shmem_filter    =FragMP4ShmemFrameFilter(shmem_name, shmem_buffers, cellsize)
mux_filter      =FragMP4MuxFrameFilter("fragmp4muxer", shmem_filter)
#mux_filter.activate()

# fork
fork_filter     =ForkFrameFilter("fork_filter", av_in_filter, mux_filter)

# main branch
livethread      =LiveThread("livethread")

"""
Define connection to camera: frames from the IP camera are written to live_out_filter and tagged with slot number 1:
"""
ctx =LiveConnectionContext(LiveConnectionType_rtsp, rtsp_adr, 1, fork_filter)
"""
Start threads:
"""
glthread.startCall()
avthread.startCall()
livethread.startCall()

# start decoding
avthread.decodingOnCall()

livethread.registerStreamCall(ctx)

# create an X-window
window_id =glthread.createWindow()
glthread.newRenderGroupCall(window_id)

# maps stream with slot 1 to window "window_id"
context_id=glthread.newRenderContextCall(1,window_id,0)

"""
Ok, the server is alive and running.  Let's do the client part for receiving frames.
"""
client = FragMP4ShmemClient(
    name=shmem_name,
    n_ringbuffer=shmem_buffers,
    n_size=cellsize,
    mstimeout=timeout,  
    verbose=False
)

"""
The client is ready to go.  Before starting to receive frames, start playing the RTSP camera
"""
livethread.playStreamCall(ctx)

"""
Throwing asyncio into the mix.  For a comprehensive treatment of the topic, please see here: https://github.com/elsampsa/valkka-examples/tree/master/example_projects/basic
"""
async def ws_handle(websocket, path):
    """This is only started upon connection
    """
    print("ws_handle at", path)
    cc = 0
    mux_filter.activate()
    mux_filter.sendMeta()
    while True:
        index, meta = client.pullFrame()
        if (index == None):
            print("timeout")
        else:
            data = client.shmem_list[index][0:meta.size]
            if meta.name in ["ftyp", "moov"]:
                print("got", meta.name)
            # print("got", meta.name, "of size", meta.size)
        await websocket.send(data.tobytes())
        cc+=1
        #if cc >= 100:
        #    break
        if cc % 100 == 0:
            print("sent", cc, "packets")
    asyncio.get_event_loop().stop()

start_server = websockets.serve(ws_handle, 'localhost', 3001)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

print("stopping..")

mux_filter.deActivate() # don't forget!
"""
Clear the server
"""
glthread.delRenderContextCall(context_id)
glthread.delRenderGroupCall(window_id)

# stop decoding
avthread.decodingOffCall()

# stop threads
livethread.stopCall()
avthread.stopCall()
glthread.stopCall()

# stop nginx reverse proxy
print("terminating nginx")
nginx_process.terminate()
nginx_process.wait()

print("bye")
