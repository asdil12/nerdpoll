#!/usr/bin/python3

import cgi, cgitb
import os
import json

print("Content-type: application/json\n")

print(json.dumps({
    "short_name": "NerdPoll",
    "name": "NerdPoll",
    "start_url": "nerdpoll.py?%s" % os.environ.get('QUERY_STRING', ''),
    "display": "standalone",
    "theme_color": "#242e3a",
    "background_color": "#242e3a"
}))

"""
    "icons": [
    {   
        "src": "favicon.ico",
        "sizes": "48x48 32x32 16x16",
        "type": "image/x-icon"
    },  
    {   
        "src": "android-chrome-192x192.png",
        "sizes": "192x192",
        "type": "image/png"
    },  
    {   
        "src": "android-chrome-512x512.png",
        "sizes": "512x512",
        "type": "image/png"
    }   
    ],  
"""
