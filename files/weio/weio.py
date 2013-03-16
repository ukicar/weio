# -*- coding: utf-8 -*-
"""
    Simple sockjs-tornado application. By default will listen on port 8080.
"""
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options

import sockjs.tornado

import subprocess
import json
import IWList
import re
import shutil
import time
import os

# Mode
AP = 0
STA_NOT_CONNECTED = 1
STA_CONNECTED = 2
WIFI_DOWN = -1


# Time needed for wifi to reconfigure (in seconds)
RECONF_TIME = 10

def WeioCommand(command) :
    output = "PLACEHOLDER"

    print(str(command))

    try :
        output = subprocess.check_output(command, shell=True)
    except :
        print("Comand ERROR : " + str(output))
        output = "ERR_CMD"
	
    print output
    return output


def WeioCheckConnection() :
    iface = "wlan0"
    command = "iwinfo " + iface +  " info"

    status = WeioCommand(command)

    print(str(status))
    # We are in STA mode, so check if we are connected
    if (status == "ERR_CMD") or "No such wireless device" in status :
        # WiFi is DOWN
        print "Wifi is DOWN"
        con = WIFI_DOWN
    # Check if wlan0 is in Master mode
    elif "Mode: Master" in status :
        print "AP Mode"
        con = AP
    elif "No station connected" in status :
        print "STA Mode : wifi is UP but not connected"
        con = STA_NOT_CONNECTED
    else :
        print "STA Mode : wifi is UP and connected!"
        con = STA_CONNECTED

    # We can not serve anything if we are not in STA_CONNECTED or AP mode
    while (con != STA_CONNECTED and con != AP) :
        # Move to Master mode
        print "Trying to move to AP mode..."
        WeioCommand("/weio/wifi_set_mode.sh ap")
        # Wait for network to reconfigure
        time.sleep(RECONF_TIME)
        # Check what happened
        con = WeioCheckConnection()

    return con

def WeioSetConnection(essid, passwd) :
    """ First shut down the WiFi on Carambola """
    WeioCommand("wifi down")
    

    """ Change the /etc/config/wireless.sta : replace the params """
    fname = "/etc/config/wireless.sta"

    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            line = re.sub(r'option\s+ssid\s.*$', r'option ssid ' + essid, line)
            line = re.sub(r'option\s+key\s.*$', r'option key ' + passwd, line)
            out.write(line)
        out.close()
        os.rename(out_fname, fname)
        shutil.copy(fname, "/etc/config/wireless")

    WeioCommand("/weio/wifi_set_mode.sh sta")


def WeioGetConfig() :
    command = "/sbin/ifconfig"
    return WeioCommand(command)


class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        htmlFile = 'static/app/app.html'
        self.render(htmlFile)

class WeioApp(sockjs.tornado.SockJSConnection):
    def on_message(self, msg):
        logging.info("App sends request")

        if msg == 'WIFI_CONF_REDIR_REQ' :
            htmlFile = 'static/wificon/wificon.html'
            self.redirect(htmlFile)
        

    def on_open(self, info):
        logging.info("App route OPEN")
        con = WeioCheckConnection()
	print (str(con))
        rsp = {};
        rsp['type'] = 'WIFI_MODE_RSP'

        if (con == AP) :
            rsp['load'] = 'AP'
        else :
            rsp['load'] = 'STA'

        self.send(json.dumps(rsp))

class WeioConnection(sockjs.tornado.SockJSConnection):
    def on_open(self, info) :
            """An iwlist scan was requested"""
            print "HEREEEEEEEEEEEEEEEEEEEEE"
            iwl = IWList.IWList("wlan0")
            #print iwl.getData()

            print type(iwl.data)
            for key in iwl.data.keys():
                print key;

            rsp={}
            rsp['type'] = 'WIFI_SCAN_RSP'
            rsp['load'] = iwl.data

            self.send(json.dumps(rsp))

    def on_message(self, msg):
        logging.info("Button pressed")
        """We have obtained essid and psswd,
        so we can try to connect"""
        
        req = json.loads(msg)

        if req['req_type'] == "WEIO_AP_REQ" :
            WeioCommand("/weio/wifi_set_mode.sh ap")
        elif req['req_type'] == "WEIO_STA_REQ" : 
            essid = req['load']['essid']
            passwd = req['load']['passwd']
            print essid
            print passwd

            WeioSetConnection(essid, passwd)
            # Wait for network to reconfigure
            time.sleep(RECONF_TIME)
        else :
            print "WeioConnection() handler : UNKNOWN REQ"

        con = WeioCheckConnection()

        #rsp={}
        #rsp['type'] = 'WIFI_CON_RSP'
        #rsp['load'] = con

        # Send connection information to the client
        #self.send(json.dumps(rsp))

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    #tornado.options.define("port", default=8080, type=int)
    tornado.options.define("port", default=80, type=int)

    # Check WiFi connection mode and status (and force AP mode if needed)
    WeioCheckConnection()

    # 1. Create weio app router
    WeioWifiCfgRouter = sockjs.tornado.SockJSRouter(WeioApp, '/app')

    # 1. Create weio wificonfig router
    WeioAppRouter = sockjs.tornado.SockJSRouter(WeioConnection, '/weio')

    # 2. Create Tornado application
    #app = tornado.web.Application(
    #        list(WeioRouter.urls) + [(r"/", IndexHandler), (r"/(.*)", tornado.web.StaticFileHandler,
	#				{"path": ".", "default_filename": "index.html"})])

    app = tornado.web.Application(
					list(WeioWifiCfgRouter.urls) + list(WeioAppRouter.urls) + [(r"/", IndexHandler), (r"/(.*)", tornado.web.StaticFileHandler,
					{"path": "./static", "default_filename": "index.html"})])

    # 3. Make Tornado app listen on port 8080
    #app.listen(8080)
    #logging.info(" [*] Listening on 0.0.0.0:8080")
    logging.info(" [*] Listening on 0.0.0.0:80")

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    #print "http://localhost:%d/static/" % tornado.options.options.port

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
