
# OUTDATED. DO NOT USE.

# Live H264 stream from RTSP camera to your browser

It this rudimentary demo we're streaming live video from an RTSP camera to your HTML5 browser.

Video is streamed as H264 video stream encapsulated in MP4.  No transcoding takes place.  No flash or pure-javascript decoders required.

Video is decoded and presented in the browser using the W3 Media Source Extensions that is well supported by all major browsers by now.

## How does it work?

Roughly like this:

    server-side                   client side
    
    ws_serve.py ==> websocket ==> ws_client.html or ws_client_new.html
    
    - FFmpeg                      - JavaScript
                                  - W3 MediaSource Extension

- Python program **ws_serve.py** is using ffmpeg as a slave process 
- It reads mp4 muxed video stream from ffmpeg's stdout

- That stream is passed through websocket to **ws_client.html**

- **NOTE**: please prefer the updated **ws_client_new.html** as it included stuff from [this stackoverflow question](https://stackoverflow.com/questions/54186634/sending-periodic-metadata-in-fragmented-live-mp4-stream/)


- Client uses the W3 Media Source Extensions to push the payload into browsers video decoding infrastructure

To try it out follow the steps ..

### 1. Install Apache2 and configure it for websockets

Install Apache2 and some additional modules for it:

    sudo apt install apache2
    sudo a2enmod userdir
    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo a2enmod proxy_wstunnel
    
Add to


    /etc/apache2/sites-available/000-default.conf
    
The following lines
    
    ProxyRequests Off 
    ProxyPass /ws/  ws://example.com:3001

Make directory for user web content
    
    cd
    mkdir public_html
    cd public_html 

Restart Apache2
    
    systemctl restart apache2
    
    
### 2. Install python dependencies

Install websocket module with

    pip3 install --user --upgrade websocket
    
### 3. Setup your files

Copy **ws_client.html** to $HOME/public_html/ws_client.html

Edit **ws_serve.py** for your ip camera address, username and password


### 4. Run it!

1. Confirm that your Apache2 is working by pointing your browser to:

    http://localhost
    
2. Start serving the websocket with:

    python3 ws_serve.py
    
3. Point your browser to (prefer the latter):

    http://localhost/~your_username/ws_client.html

    http://localhost/~your_username/ws_client_new.html


Live video rolls for a minute or so, until it stops.

.. because, when reading ffmpeg stdout, the mp4 boxes should be reconstructed from
fragments.

If you want a more serious solution, please see [this](https://elsampsa.github.io/valkka-examples/_build/html/cloud.html) and [this](https://github.com/elsampsa/valkka-examples/tree/master/example_projects/basic)

Other problems might arise if your video also includes audio (for tips, see the ws_client_new.html)

## License 

MIT

## Copyright

Copyright 2018 Sampsa Riikonen

## Author

Sampsa Riikonen

