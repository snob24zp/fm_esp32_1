#!/usr/bin/python3

import time
import sys
import json
import xml.etree.ElementTree as xml_parser
import paho.mqtt.client as paho

def gen_list(CWD):
    releases = {}

    with open(f'{CWD}/releases.json') as f:
        releases = json.load(f)

    out = []

    for r in releases.keys():
        fwpath = releases[r].split('/')[0]
        cur = None
        with open(f'{CWD}/{fwpath}/release.json') as f:
            cur = json.load(f)

        fw_root = xml_parser.parse(f'{CWD}/{releases[r]}').getroot()
        chunks = len(fw_root.find("chunks"))
        out.append({
            "r": cur['release'],
            "b": cur['branch'],
            "c": cur['commit'],
            "s": chunks
        })

    return out


def iterate_devs(path):
    with open(f'{path}/devices.json') as f:
        js = json.load(f)
        for k in js:
            yield k, js[k]


def retain_publish(cl, tp, msg):
    print(f'Publish [ type: {tp}, msg: {msg} ]')
    cl.publish(f">updater/list/{tp}", json.dumps(msg), retain=True, qos=1)


if __name__ == "__main__":
    argv = sys.argv[1:]
    path = argv[0] if len(argv) > 0 else  '/var/www/release'
    print(f'Use path: {path}')
    cl= paho.Client("upd-announcer")
    cl.loop_start()
    cl.connect('x.ks.ua',1883)
    for (k, v) in iterate_devs(path):
        retain_publish(cl, k,  gen_list(f'{path}/{v}'))
        time.sleep(1)

    cl.disconnect()
    cl.loop_stop()