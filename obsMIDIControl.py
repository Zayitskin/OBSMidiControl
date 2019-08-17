import json, os
import obspython as obs
from multiprocessing import Process, SimpleQueue, set_executable
from midoWrapper import midiControl

def script_description():
    return "Script for facilitating control of OBS through MIDI messages"

def script_load(settings):
    global q, p
    print("obsPygameControl initalized!")
    if os.name == "nt":
        set_executable("F:\\No Mans Land\\Python36\\python.exe")
    device = obs.obs_data_get_string(settings, "deviceName")
    if device == "":
        device = None
    q = SimpleQueue()
    p = Process(target = midiControl, args = (q, device,))
    p.start()

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
    p.terminate()
    print("Shutting down.")

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_path(props, "configFile", "JSON Config File", obs.OBS_PATH_FILE, "*.json", None)
    obs.obs_properties_add_text(props, "deviceName", "Midi Device Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(props, "midiRefresh", "Refresh Midi Device Connection", restartProcess)

    return props

def script_tick(seconds):
    try:
        while not q.empty():
            parse(q.get())
    except NameError:
        pass

def restartProcess(props, prop):
    p.terminate()
    device = obs.obs_data_get_string(settings, "deviceName")
    if device == "":
        device = None
    q = SimpleQueue()
    p = Process(target = midiControl, args = (q, device,))
    p.start()
    

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
        repr(e)
    

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
