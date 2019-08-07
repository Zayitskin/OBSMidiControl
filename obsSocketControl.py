#import mido
import socket

import json
import obspython as obs

def script_description():
    return "Script for facilitating control of OBS through MIDI messages"

def script_load(settings):
    global sock
    sock = None
    print("obsSocketControl initialized!")

def script_update(settings):
    global config
    path = obs.obs_data_get_string(settings, "configFile")
    config = None

    if path != "":
        with open(path, "r") as f:
            data = json.load(f)
            config = {}
            for obj in data:
                if obj["key"] not in config.keys():
                    config[obj["key"]] = {obj["value"]: []}
                elif obj["value"] not in config[obj["key"]].keys():
                    config[obj["key"]][obj["value"]] = []
                config[obj["key"]][obj["value"]].extend(obj["commands"])
            print(config)

def script_unload():
    if sock != None:
        sock.close()
    print("Socket closed and script ended.")

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "configFile", "JSON Config File", obs.OBS_PATH_FILE, "*.json", None)
    obs.obs_properties_add_button(props, "connectSocket", "Connect to test server", connect)
    

    return props

def script_tick(seconds):
    global sock
    if sock != None:
        try:
            msg = sock.recv(1024)
            parse(msg.decode("utf-8"))
        except BlockingIOError:
            pass
        except ConnectionResetError:
            sock.close()
            sock = None
            print("Socket externally reset.")
        except OSError as e:
            print("Message error: " + str(e))
            sock = None
            
def connect(props, prop):
    global sock
    try:
        sock = socket.socket()
        sock.connect(("localhost", 50007))
        sock.setblocking(False)
    except (ConnectionAbortedError, ConnectionRefusedError, OSError) as e:
        sock = None
        print("Connection failed: " + str(e))

def parse(msg):
    try:
        key, value = msg.split(" ")
        print(key + " " + value)
        value = int(value)
    except ValueError:
        return
    
    try:
        commands = config[key][value]
        for command in commands:
            if command["type"] == "toggle":
                toggle(command["target"])
            elif command["type"] == "transition":
                transition(command["target"])
    except KeyError as e:
        return
    

def toggle(source):
    print("Toggle: " + source)
    scene = obs.obs_frontend_get_current_scene()
    sceneitem = obs.obs_scene_find_source(obs.obs_scene_from_source(scene), source)
    obs.obs_sceneitem_set_visible(sceneitem, not obs.obs_sceneitem_visible(sceneitem))
    obs.obs_source_release(scene)

def transition(scene):
    print("Transition: " + scene)
    scenes = obs.obs_frontend_get_scenes()
    for s in scenes:
        if obs.obs_source_get_name(s) == scene:
            obs.obs_frontend_set_current_scene(s)
        obs.obs_source_release(s)
