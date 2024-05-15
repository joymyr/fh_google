import asyncio
import json
import time

import requests
from typing import List
import paho.mqtt.client as mqtt

from const import *
from device import Device

devices: List[Device] = []
updateAll = False
mqclient = mqtt.Client()


async def main() -> None:
    google_init()
    mq_init()
    await update_loop()


def mq_init() -> None:
    mqclient.on_connect = on_connect
    mqclient.on_message = on_message

    mqclient.loop_start()
    mqclient.username_pw_set(MQ_USERNAME, MQ_PASSWORD)
    mqclient.connect(MQ_ADDRESS, MQ_PORT, 60)


def google_init() -> None:
    response = requests.get(f"{CAST_URL}device/")

    global devices
    for dev in response.json():
        print(f"add {dev['name']} ({dev['id']})")
        devices.append(Device(dev["id"], dev["name"]))
    devices.sort(key=lambda x: x.device_id)


async def update_loop() -> None:
    while True:
        google_to_fh_update_all()
        time.sleep(UPDATE_EVERY_SECONDS)

# The callback for when the client receives a CONNECT response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQ_MAIN_TOPIC)

    google_to_fh_add_all()


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"Handling message - Topic: {msg.topic}, Payload: {str(msg.payload)}")
    try:
        payload = json.loads(msg.payload)
        val = payload["val"]
        assistant_topic = f"{MQ_SIREN_COMMAND_TOPIC}/ad:g1_0"

        if msg.topic == MQ_MAIN_TOPIC:
            google_to_fh_update_all()
        elif msg.topic == assistant_topic:
            response = requests.post(f"{CAST_URL}assistant/command", json={
                "message": val
            })
            print(f"Response {response.status_code} - {response.text}")
        else:
            for device in devices:
                siren_topic = f"{MQ_SIREN_COMMAND_TOPIC}/ad:g{device.device_id}_0"
                media_topic = f"{MQ_MEDIA_COMMAND_TOPIC}/ad:g{device.device_id}_1"
                if msg.topic == siren_topic:
                    response = requests.get(f"{CAST_URL}device/{device.device_id}/stop") if val == "off" \
                        else requests.post(f"{CAST_URL}device/{device.device_id}/playMedia", json=[{
                            "mediaTitle": val,
                            "googleTTS": "no-NO"
                        }])
                    print(f"Response {response.status_code} - {response.text}")
                elif msg.topic == media_topic:
                    response = requests.get(f"{CAST_URL}device/{device.device_id}/volume/{val}") if type(val) == int \
                        else requests.get(f"{CAST_URL}device/{device.device_id}/{val}")
                    print(f"Response {response.status_code} - {response.text}")
    except Exception as err:
        print(f"Failed to handle message {err}, {type(err)} - Topic: {msg.topic}, Payload: {str(msg.payload)}")


def google_to_fh_add_all() -> None:
    google_to_fh_add_assistant()
    for device in devices:
        print(f"{device.device_name} ({device.device_id})")
        google_to_fh_add_speaker(device)


def google_to_fh_update_all() -> None:
    print("Updating all devices...")
    try:
        response = requests.get(f"{CAST_URL}device/")

        for dev in response.json():
            event_topic_siren = f"pt:j1/mt:evt{MQ_SIREN_EVENT_TOPIC}/ad:g{dev['id']}_0"
            event_topic_media = f"pt:j1/mt:evt{MQ_MEDIA_EVENT_TOPIC}/ad:g{dev['id']}_1"
            print(f"update {dev['name']} ({dev['id']})")
            mqclient.publish(event_topic_siren, payload=json.dumps({
                "serv": "siren_ctrl",
                "type": "evt.mode.report",
                "val": "off" if dev['status']['status'] == "" and dev['status']['title'] == "" and dev['status']['application'] == "" else "playback",
                "val_t": "string"
            }))
            mqclient.publish(event_topic_media, payload=json.dumps({
                "serv": "media_player",
                "type": "evt.volume.report",
                "val": int(dev['status']['volume']),
                "val_t": "int"
            }))
            mqclient.publish(event_topic_media, payload=json.dumps({
                "serv": "media_player",
                "type": "evt.playback.report",
                "val": "play" if dev['status']['status'] == "PLAYING" else "pause" if dev['status']['application'] != "" or dev['status']['title'] != "" else "stop",
                "val_t": "string"
            }))
            mqclient.publish(event_topic_media, payload=json.dumps({
                "serv": "media_player",
                "type": "evt.metadata.report",
                "val": {"track": dev['status'].get('title', ""),
                        "artist": dev['status'].get('subtitle', ""),
                        "album": dev['status'].get('application', ""),
                        "image": dev["status"].get('image_url', "")},
                "val_t": "str_map"
            }))
    except Exception as err:
        print(f"Failed to update devices {err}, {type(err)}")


def google_to_fh_add_assistant():
    event_topic_assistant = f"{MQ_SIREN_EVENT_TOPIC}/ad:g1_0"
    mqclient.subscribe("pt:j1/mt:cmd" + event_topic_assistant)
    mqclient.publish(MQ_INCLUSION_TOPIC, payload=json.dumps({
        "serv": "google",
        "type": "evt.thing.inclusion_report",
        "val_t": "object",
        "val": {
            "address": f"g1",
            "product_hash": "00001",
            "comm_tech": "google",
            "product_name": "Assistant",
            "manufacturer_id": "Google",
            "hw_ver": "1",
            "is_sensor": "0",
            "power_source": "ac",
            "services": [
                {
                    "name": "siren_ctrl",
                    "address": event_topic_assistant,
                    "enabled": True,
                    "interfaces": [
                        {"intf_t": "out", "msg_t": "evt.mode.report", "ver": "1", "val_t": "string"},
                        {"intf_t": "in", "msg_t": "cmd.mode.set", "ver": "1", "val_t": "string"},
                    ],
                    "groups": ["ch_0"],
                    "props": {
                        "sup_modes": ["on", "off", "fire", "CO", "intrusion", "door"],
                    }
                },
            ]
        },
        "src": "fh-google",
        "ver": "1",
        "uid": "00001",
        "topic": MQ_INCLUSION_TOPIC
    }))


def google_to_fh_add_speaker(device):
    event_topic_siren = f"{MQ_SIREN_EVENT_TOPIC}/ad:g{device.device_id}_0"
    event_topic_media = f"{MQ_MEDIA_EVENT_TOPIC}/ad:g{device.device_id}_1"
    mqclient.subscribe("pt:j1/mt:cmd" + event_topic_siren)
    mqclient.subscribe("pt:j1/mt:cmd" + event_topic_media)
    mqclient.publish(MQ_INCLUSION_TOPIC, payload=json.dumps({
        "serv": "google",
        "type": "evt.thing.inclusion_report",
        "val_t": "object",
        "val": {
            "address": f"g{device.device_id}",
            "product_hash": device.device_id,
            "comm_tech": "google",
            "product_name": device.device_name,
            "manufacturer_id": "Google",
            "hw_ver": "1",
            "is_sensor": "0",
            "power_source": "ac",
            "services": [
                {
                    "name": "siren_ctrl",
                    "address": event_topic_siren,
                    "enabled": True,
                    "interfaces": [
                        {"intf_t": "out", "msg_t": "evt.mode.report", "ver": "1", "val_t": "string"},
                        {"intf_t": "in", "msg_t": "cmd.mode.set", "ver": "1", "val_t": "string"},
                    ],
                    "groups": ["ch_0"],
                    "props": {
                        "sup_modes": ["on", "off", "fire", "CO", "intrusion", "door", "playback"],
                    }
                },
                {
                    "name": "media_player",
                    "address": event_topic_media,
                    "enabled": True,
                    "interfaces": [
                        {"intf_t": "out", "msg_t": "evt.volume.report", "ver": "1", "val_t": "int"},
                        {"intf_t": "in", "msg_t": "cmd.volume.set", "ver": "1", "val_t": "int"},
                        {"intf_t": "out", "msg_t": "evt.playback.report", "ver": "1", "val_t": "string"},
                        {"intf_t": "in", "msg_t": "cmd.playback.set", "ver": "1", "val_t": "string"},
                        {"intf_t": "out", "msg_t": "evt.metadata.report", "ver": "1", "val_t": "str_map"},
                    ],
                    "groups": ["ch_1"],
                    "props": {
                        "sup_playback": ["play", "pause", "stop", "next_track", "previous_track"]
                    },
                }
            ]
        },
        "src": "fh-google",
        "ver": "1",
        "uid": device.device_id,
        "topic": MQ_INCLUSION_TOPIC
    }))


asyncio.run(main())
