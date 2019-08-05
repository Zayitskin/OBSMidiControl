import mido

import json
import obspython as obs

def script_description():
    return "Script for facilitating control of OBS through MIDI messages"

def script_load(settings):
    global port
    port = mido.open_input("X-TOUCH COMPACT:X-TOUCH COMPACT MIDI 1 16:0")
    print(port)

def script_update(settings):
    global config
    path = obs.obs_data_get_string(settings, "configFile")
    config = None

    if path != "":
        with open(path, "r") as f:
            config = json.load(f)

def script_unload():
    global port
    if port != None:
        port.close()
    print("Job done")

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "configFile", "JSON Config File", obs.OBS_PATH_FILE, "*.json", None)
    

    return props

def script_tick(seconds):
    global port
    try:
        if port != None:
            for msg in port.iter_pending():
                parse(msg)
    except NameError:
        pass
            

def parse(msg):
    data = msg.dict()
    for source in config.keys():
        if config[source]["type"] == data["type"] and config[source]["value"] == data["note"]:
            toggle(source)

def toggle(source):
    scene = obs.obs_frontend_get_current_scene()
    sceneitem = obs.obs_scene_find_source(obs.obs_scene_from_source(scene), source)
    obs.obs_sceneitem_set_visible(sceneitem, not obs.obs_sceneitem_visible(sceneitem))
    
    obs.obs_source_release(scene)
    obs.obs_source_release(sceneitem)
