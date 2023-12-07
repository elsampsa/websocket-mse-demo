
# Live H264 stream from RTSP camera to your browser

**WARNING** *This repo is obsolete (and has some bugs), please use instead* https://github.com/elsampsa/valkka-streamer

* * * * 

*a new, completely rewritten version!*

It this demo we're streaming live video from an RTSP camera to your HTML5 browser.

Video is streamed as H264 encapsulated in MP4.  No transcoding takes place in the stream-to-browser pipeline.  No browser-side flash or pure-javascript decoders required.

Video is decoded and presented in the browser using the W3 Media Source Extensions that is well supported by all major browsers by now.

Only H264 is supported - browser MSE's do not support H246 yet (and neither does libValkka).

## How does it work?

Roughly like this:

```
server-side                                   nginx
    
ws_serve_new.py <-- websocket <---------------+-* <----+  <---- web browser        
                                              |        |
                    ws_client_new.html  <-----+        |
                            |                          |
                            +--------------------------+
                                  (requests websocket)

Starts nginx
Uses libValkka                     JavaScript
                                   W3 MediaSource Extension
```

The web-browser client uses the W3 Media Source Extensions to push the payload into browsers video decoding infrastructure.

## Requirements

- Install libValkka as instructed [here](https://elsampsa.github.io/valkka-examples/_build/html/requirements.html)
- Install nginx with ``sudo apt-get install nginx``
- Install python websocket module with ``pip3 install --user websockets``
- Prepare nginx user rights:
```
sudo addgroup nginx
sudo chgrp nginx /var/lib/nginx
sudo adduser $USER nginx
sudo chmod g+r+w+x /var/lib/nginx
```
- You need to do logout/login (so that group change takes effect)
- Test if your nginx works correctly
```
nginx -p $PWD -c ./nginx.conf -g 'error_log error.log warn;'
```

- Setup your camera so that it sends H264 only.

## Usage

### 1. Start the program with
```
killall -9 nginx; python3 ws_serve_new.py rtsp://user:password@ip-address
```
An X-window is opened that shows you the live video stream.

### 2. Open your browser 
Your low-latency live video is now available at [http://localhost:8089](http://localhost:8089)

## Now what?

- Please tell me in the issues if this worked for you or not and what camera & other setup you are using
- ..i.e. don't just report the bugs, but also successes!  :)
- If you want a more serious solution, please see [this](https://elsampsa.github.io/valkka-examples/_build/html/cloud.html) and [this](https://github.com/elsampsa/valkka-examples/tree/master/example_projects/basic)

## References

- [frag-mp4 stackoverflow question](https://stackoverflow.com/questions/54186634/sending-periodic-metadata-in-fragmented-live-mp4-stream/)
- [frag-mp4 with libValkka](https://elsampsa.github.io/valkka-examples/_build/html/cloud.html)

## License 

MIT

## Copyright

Copyright 2018-2020 Sampsa Riikonen

## Author

Sampsa Riikonen

