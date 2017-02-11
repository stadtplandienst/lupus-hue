#!/usr/bin/env python3.4

import requests, json, pprint, time, socket, http.client, io, configparser, os, sys

from   http.server import BaseHTTPRequestHandler, HTTPServer
from   multiprocessing import Process, Pipe

global parent_conn
global child_conn
global lux
global deferred_groups
global my_scenes
global base_url

class SSDPResponse(object):
    # Find Hue bridge via SSDP multicast
    class _FakeSocket(io.BytesIO):
        def makefile(self, *args, **kw):
            return self
    def __init__(self, response):
        r = http.client.HTTPResponse(self._FakeSocket(response))
        r.begin()
        self.location = r.getheader("location")
        self.host = r.getheader("host")
        self.usn = r.getheader("usn")
        self.st = r.getheader("st")
        self.server = r.getheader("server")
        self.cache = r.getheader("cache-control").split("=")[1]
    def __repr__(self):
        return "<SSDPResponse({location}, {st}, {usn})>".format(**self.__dict__)

def discover(service, timeout=5, retries=1, mx=3):

    bridge_ip = "" 
    group = ("239.255.255.250", 1900)
    message = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        'HOST: {0}:{1}',
        'MAN: "ssdp:discover"',
        'ST: {st}','MX: {mx}','',''])
    socket.setdefaulttimeout(timeout)
    responses = {}
    for _ in range(retries):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        message_bytes = message.format(*group, st=service, mx=mx).encode('utf-8')
        sock.sendto(message_bytes, group)
        while True:
            try:
                response = SSDPResponse(sock.recv(1024))
                if "IpBridge" in response.server:
                    if bridge_ip == "":
                        bridge_ip = response.location[7:21]
                responses[response.location] = response
            except socket.timeout:
                break
    return bridge_ip

def init_scenes(do_print,do_delete):

    global j_groups
    global my_scenes
    global base_url
    global group_names
    global port

    # Read config file
    config = configparser.ConfigParser()
    file = 'lupus-hue.conf'
    
    if os.path.exists(file):
        config.read(file)
        bridge_ip = ""
        bridge_user = ""
        try:
            bridge_ip = config["Hue"]["bridge_ip"]
            bridge_user = config["Hue"]["bridge_user"]
            port = int(config["HTTP-Server"]["port"])
        except:
            print ("Error in [Hue] or [HTTP-Server] section in config file.",file)
            sys.exit()
            
        if bridge_ip == "":
            print ("Bridge IP not configured. Scanning for Hue bridge ...")
            bridge_ip = discover("ssdp:all")
            if bridge_ip == "":
                print ("No Hue bridge found!")
                sys.exit()
            config["Hue"]["bridge_ip"] = bridge_ip
            with open(file, 'w') as configfile:
                config.write(configfile)
        if (do_print):
            print ("Hue bridge IP is:",bridge_ip)
            
        if bridge_user == "":
            payload = {"devicetype": "lupus-hue#server"}
            print ("Creating new Hue user. Press link button on bridge!")
            for i in range(20):
                resp = requests.post("http://"+bridge_ip+"/api",data=json.dumps(payload))
                r = resp.json()
                try:
                    bridge_user = r[0]["success"]["username"]
                    print ("Link button was pressed.")
                    break
                except:
                    pass
                time.sleep(1)
            if bridge_user == "":
                print ("Error while linking with bridge:",r[0])
                sys.exit()
            config["Hue"]["bridge_user"] = bridge_user
            with open(file, 'w') as configfile:
                config.write(configfile)
        base_url = "http://"+bridge_ip+"/api/"+bridge_user+"/"
    else:
        print ("Config file",file,"not found.")
        sys.exit()

    # Get groups and store in global variable
    resp = requests.get(base_url+"groups/")
    j_groups = resp.json()

    # Get scenes
    resp = requests.get(base_url+"scenes/")
    scenes = resp.json()

    group_names = config["Groups"]
    config_scenes = config["Scenes"]
    config_lightstates = config ["Lightstates"]

    my_scenes = { }

    if True:
        for s in config_scenes:
            entries = config_scenes[s].split(' ')
            light_list = []
            lightstate_list = []
            my_scenes[s] = { "id": "" }
            for e in entries:
                try:
                    params = e.split(':')
                    state = params[0].lstrip(' ')
                    lights = params[1].split(',')
                    for light in lights:
                        light_list.append(light)
                        state_list = config["Lightstates"][state].split(' ')
                        lst = {}
                        for st in state_list:
                            try:
                                params = st.split(':')
                                key = params[0].lstrip(' ')
                                vs = params[1].lstrip(' ')
                            except:
                                print ("Error in config file. Wrong state definition:",st)
                                sys.exit()
                            if key in ("bri", "hue", "sat","transitiontime", "ct"):
                                value = int(vs)
                            elif key in ("on"):
                                value = vs == "true" or vs == "True"
                            else:
                                value = vs
                            # print ("key",key,"value",value)
                            lst[key] = value
                        lightstate = { "light": light, "state": lst }
                        # print ("state",state,"lightstate",lightstate)
                        lightstate_list.append(lightstate)
                except:
                    print ("Error in config file:",e)
                    sys.exit()
            my_scenes[s]["lights"] = light_list
            my_scenes[s]["lightstates"] = lightstate_list
    else:
        print ("Wrong paramater(s) in config file.")

    # Delete prexisting scenes
    if (do_delete):
        for s_id in scenes:
            # print (s_id)
            s_details = scenes[s_id]
            for m in my_scenes:
                if m == s_details["name"]:
                    print ("Deleting scene "+m+".")
                    payload = {}
                    resp = requests.delete(base_url+"scenes/"+s_id,data=json.dumps(payload))
                    result = resp.json()
                    try:
                        print ("Error deleting scene:",rj[0]["error"])
                    except:
                        pass

    # Checking whether scenes already exist
    for s_id in scenes:
        s_details = scenes[s_id]
        for m in my_scenes:
            if m == s_details["name"]:
                d = my_scenes[m]
                my_scenes[m] = { "id": s_id, "lights": d["lights"], "lightstates": d["lightstates"] }

    # Create scenes that do not exit
    for m in my_scenes:
        if my_scenes[m]["id"] == "":
            # Create scene
            payload = {"name": m, "lights": my_scenes[m]["lights"], "recycle": False }
            try:
                resp = requests.post(base_url+"scenes/",data=json.dumps(payload))
                rj = resp.json()
                my_scenes[m]["id"] = rj[0]["success"]["id"]
            except:
                print ("Error while creating scene:",rj[0]["error"])

    # Set lightstates for all my scenes
    for m in my_scenes:
        for ls in my_scenes[m]["lightstates"]:
            payload = ls["state"]
            resp = requests.put(base_url+"scenes/"+my_scenes[m]["id"]+"/lightstates/"+ls["light"] \
                              ,data=json.dumps(payload))
            rj = resp.json()
            try:
                print ("Error setting lightstates:",rj[0]["error"])
            except:
                continue

    return

def zeit (time):
    if int(time/60) == 0:
        message = str(time) + " seconds"
    elif int(time/60) == 1:
        message = "1 minute"
    else:
        message = str(int(time/60)) + " minutes"
    return message
                        
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):
  
    def do_GET(self):
        
        global lux
        global init
        global j_groups
        global my_scenes
        global base_url
        global group_names

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        message = "<html><head><title>lupus-hue server</title></head><body>"     


        if 1:
        # try:
                 
            params = { "l":"","g":"","d":"","b":"","h":"","s":"","t":"","x":"","c":"","n":""}
      
            param = self.path.split("?")
            action = param[0].lstrip('/')

            try:
                args = param[1].split("_")
                for a in args:
                    arg = a.split("=")
                    params[arg[0]] = arg[1]
            except:
                pass
            
            number_list = []
            
            if not init:
                init = True
                init_scenes(False,False)
                # print (base_url)

            payload = {}

            # Process params of request
            if params["g"] == "all":
                number_list.append("0")

            if params["l"] != "":
                number_list.append(params["l"])
                is_light = True
            else:
                is_light = False
                for x in range(99):
                    try:
                        y = j_groups[str(x+1)]
                        if action == "info":
                            message += "group " + str(x+1) + " = " + y["name"] + "<br>"
                        if params["g"] == y["name"]:
                            number_list.append(str(x+1))
                        elif y["name"] in group_names[params["g"]]:
                            number_list.append(str(x+1))
                    except:
                        pass
      
            if params["t"] != "":
                is_timer = True
                tim = int(params["t"])
            else:
                tim = 0
                is_timer = False
            
            message += "<span style=color:#071BF4>"               
            
            if params["b"] != "":
                if params["b"][0] == '+' or params["b"][0] == '-':
                    payload["bri_inc"] = int(params["b"])
                else:
                    payload["bri"] = int(params["b"])

            if params["h"] != "":
                payload["hue"] = int(params["h"])

            if params["s"] != "":
                payload["sat"] = int(params["s"])
            
            if params["c"] != "":
                payload["ct"] = int(params["c"])

            if params["x"] != "":
                lux_level = int(params["x"])
            else:
                lux_level = 99
       
            if action == "off":
                payload["on"] = False

            if action == "on":
                if params["n"] == "":
                    payload["on"] = True
                else:
                    payload["scene"] = my_scenes[params["n"]]["id"]
                
            if action == "lux":
                if lux_level != lux:
                    lux = lux_level
                    print ("Lux set to ",lux)
                    message += "Lux set to " + str(lux) + "<br>"
                    for d in deferred_groups:
                        if deferred_groups[d][0] >= lux:
                            print ("Switching on deferred group(s)"+d+".")
                            message += "Switching on deferred group(s) " + d + "<br>"
                            resp = requests.put(base_url+"groups/"+d+"/action/", \
                                data=json.dumps(deferred_groups[d][1]))
                            deferred_groups[d][0] = -1
                else:
                    message += "Lux not changed<br>"                   

            if params["d"] != "":
                is_deferred = True
                lux_level = int(params["d"])
            else:
                is_deferred = False
            
            if action == "on" and is_deferred and lux > lux_level:
                # defer switching on until dark enough
                for n in number_list:
                    print ("Defer switching of group",n,"until lux level",params["x"]+".")
                    message += "Defer switching of group " + str(n) + " until lux level " + \
                               params["x"] + "<br>"
                    deferred_groups[n] = [lux_level,payload]
                number_list = []
                         
            if action == "info":
                child_conn.send(["info","",-1,False,""])

            if action == "init":
                init_scenes(False,True)
            
            for x in number_list:
                if lux <= lux_level:
                    # Either brightness is irrelevant (no lux param) or it is dark enough
                    if action == "loop":
                        # Kill potential timer for group 
                        child_conn.send(["group",x,-1,False,""])
                        # Send loop command
                        child_conn.send(["loop",x,tim,False,params["n"]])
                        message += "loop started for group " + x + " and scene " + params["n"] + " for " + zeit(tim)
                        continue
                    elif action == "info":
                        if params["n"] != "":
                            resp = requests.get(base_url+"scenes/")
                        else:
                            if is_light:
                                resp = requests.get(base_url+"lights/"+x)
                            else:
                                resp = requests.get(base_url+"groups/"+x)
                    else: # Action is on or off
                        # print ("Action",x,action,is_timer)
                        if not is_timer:
                            # Kill potential previous timer
                            if is_light:
                                child_conn.send(["light",x,-1,False,""])
                            else:
                                child_conn.send(["group",x,-1,False,""])
                        # Perform on or off action
                        if not is_light:
                            resp = requests.put(base_url+"groups/"+x+"/action/",data=json.dumps(payload))
                            # Delete potentially deferred group
                            delete_deferred(x)
                        else:
                            resp = requests.put(base_url+"lights/"+x+"/state/",data=json.dumps(payload))
                            
                        if is_timer:
                            # Action was performed so now start timer to switch off or on later
                            if is_light:
                                command = "light"
                            else:
                                command = "group"
                            if action == "on":
                                child_conn.send([command,x,tim,False,""])
                            else:
                                child_conn.send([command,x,tim,True,""])
                            if is_light:
                                message += "Timer set for light " + x + ": " + zeit(tim) + "<br>"
                            else:
                                message += "Timer set for group " + x + ": " + zeit(tim)+ "<br>"
                                
   
                    pp = pprint.pformat(resp.json(),indent=4)
                    result = str(pp)
                    result = result.replace("\n","<br>")
                    result = result.replace("{","")
                    result = result.replace("}","")
                    result = result.replace(",","")
                    result = result.replace("'","")
                    result = result.replace(" ","&nbsp;")
                    message += result
                    message += "<br>"
                else:
                    print ("Command for group/light ",x, " not executed because of lux level.")
        else:
        # except:
            message += "<span style=color:#F40707>"
            message += "wrong param(s) exception</body></html>"
            print ("Wrong param(s) exception")
         
        message += "</body></html>"
        self.wfile.write(bytes(message,"utf8"))
        
        return
    
def delete_deferred (g):
    
    for d in deferred_groups:
        try:
            if deferred_groups[g][0] >= 0:
                deferred_groups[g][0] = -1
                print ("Deleted deferred group ",g+".")
        except:
            pass
    return
    
def run (conn):
    
    lux = 0
    global init
    global port

    init = False
    
    # Server settings
    server_address = ('',port)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print ('HTTP server: ',myHTTPServer_RequestHandler.server_version, \
           myHTTPServer_RequestHandler.sys_version,"port/"+str(port))
    httpd.serve_forever()

def switch(group,lights,on):

    global base_url 
    payload = ({"on" : on })

    try:
        if lights:
            resp = requests.put(base_url+"lights/"+group+"/state/",data=json.dumps(payload))
        else:
            resp = requests.put(base_url+"groups/"+group+"/action/",data=json.dumps(payload))
    except:
        print ("Exception in switch()")
    
    return

def blink(scene,timer,group):

    global base_url

    try:
        if (timer == 0):
            n = scene + "3"
            payload = {"scene": my_scenes[n]["id"] }
            resp = requests.put(base_url+"groups/"+group+"/action/",data=json.dumps(payload))
        else:
            if (timer % 2 != 0):
                n = scene + "1"
                payload = {"scene": my_scenes[n]["id"] }
                resp = requests.put(base_url+"groups/"+group+"/action/",data=json.dumps(payload))
            else:
                n = scene + "2"
                payload = {"scene": my_scenes[n]["id"] }
                resp = requests.put(base_url+"groups/"+group+"/action/",data=json.dumps(payload))
    except:
        print ("Exception in blink(). Probably wrong scene name provided.")
    return

if __name__ == '__main__':

    global base_url
    global j_groups
    global my_scenes

    print ("++++ lupus-hue server")

    init_scenes(True,False)

    # Creating pipe
    parent_conn, child_conn = Pipe()

    lux = 0
    deferred_groups = { }
    
    p = Process(target=run, args=(child_conn,))
    p.start()

    # Start receiving loop for switching off groups and lights after a certain time
    groups_state = { }
    lights_state = { }
    loops_state = { }


    timeout = 1  # Wait cycle in seconds

    while True:
        if True:
            for p in groups_state.keys():
                if groups_state[p][0] > 0:
                    # decrease counter
                    groups_state[p][0] -= 1
                    if groups_state[p][0] == 0:
                        if groups_state[p][1]:
                            o = "on"
                        else:
                            o = "off"
                        print ("Timer: switching group", p, o)
                        switch(p,False,groups_state[p][1])
                # print ("grp ",p, groups_state[p][0],groups_state[p][1])

            for p in lights_state.keys():
                if lights_state[p][0] > 0:
                    # decrease counter
                    lights_state[p][0] -= 1
                    if lights_state[p][0] == 0:
                        if lights_state[p][1]:
                            o  = "on"
                        else:
                            o = "off"
                        print ("Timer: switching light", p, o)
                        switch(p,True,lights_state[p][1])
                # print ("lig ",p, lights_state[p][0],lights_state[p][1])

            for p in loops_state.keys():
                if loops_state[p][0] > 0:
                    # decrease counter
                    loops_state[p][0] -= 1
                    blink(p,loops_state[p][0],loops_state[p][1])
                    if loops_state[p][0] == 0:
                        print ("Loop: stopped group", loops_state[p][1], "scene", p)
                # print ("loop ",p, loops_state[p][0],loops_state[p][1])

            
            if parent_conn.poll(timeout):
                while parent_conn.poll(1):
                
                    params = parent_conn.recv()
                    command = params[0]
                    name = params[1]
                    time = params[2]
                    switch_off = params[3]
                    scene = params[4]
                
                    if command == "light":
                        if time == -1 and lights_state.get(name,[0,False])[0] > 0:
                            print ("Timer: light " + name + " cancelled")
                            lights_state[name] = [0,False]
                        elif time > 0:
                            print ("Timer: started for light", name, "for", zeit(time))
                            lights_state[name] = [time,switch_off]
                    elif command == "group":
                        if time == -1 and groups_state.get(name,[0,False])[0] > 0:
                            print ("Timer: group " + name + " cancelled")
                            groups_state[name] = [0,False]
                        elif time > 0:
                            print ("Timer: started for group " + name + " for " + zeit(time))
                            groups_state[name] = [time,switch_off]
                    elif command == "loop":
                        print ("Loop: started for group " + name + " and scene " + scene +" for "+zeit(time))
                        loops_state[scene] = [time,name]
                    #elif command == "info":
                    #    print ("Timer: Lights ",lights_state)
                    #    print ("Timer: Groups ",groups_state)
                    #    print ("Timer: Loops ",loops_state)

        else:
            print ("Exception")
            time.sleep(1)

    p.join()
