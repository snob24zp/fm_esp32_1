#!/usr/bin/python3

import sys
import json
import os.path
from threading import Timer
import xml.etree.ElementTree as xml_parser
from arg_parser import Args
import time
import paho.mqtt.client as mqtt


def fw_info(fw_root):
    print("Found firmware for: "+fw_root.find("fw").find("device").text)
    print("Version: "+fw_root.find("fw").find("version").text +
          " (built: "+fw_root.find("fw").find("date").text+")")
    if xml_parser.iselement(fw_root.find("fw").find("branch")):
        print("GIT Branch: "+fw_root.find("fw").find("branch").text)
    if xml_parser.iselement(fw_root.find("fw").find("commit")):
        print("GIT Commit: "+fw_root.find("fw").find("commit").text)


class pyhlo:
    def __init__(self, args, raw_fw):
        self.client = mqtt.Client()
        self.args = args
        self.raw_fw = raw_fw
        print("Connecting to: "+self.args.broker )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.args.broker)
        self.error_cnt = 0
        self.elapsed = 0
        self.prevoius_idx = 0
        
    def loop_forever(self):
        self.client.loop_forever()

    def on_connect(self, cl, userdata, flags, rc):
        print("Connected with result code: %d " % rc)
        self.client.subscribe(f"<{self.args.device}/fw_pkg")
        self.client.subscribe(f"<{self.args.device}/fw_upd")
        print("\r\nStart uploading..")
        self.elapsed = time.perf_counter()
        self.client.publish(f">{self.args.device}/fw_upd", '1', qos=1)
        self.client.publish(f">{self.args.device}/fw_pkg", f'"{self.raw_fw[0]}"', qos=1)
        self.exit_tmr = Timer(30.0,self.exit, args=[2])
        self.exit_tmr.setDaemon(True)
        self.exit_tmr.start()

    def _err_cnt_inc(self):
        self.error_cnt += 1
        if self.error_cnt > 10:
            print("\r\nError happend, exiting")
            self.exit(1)

    def print_progress (self, iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
        # Print New Line on Complete
        if iteration == total: 
            print()

    def exit(self, ret = 0):
        print(f"Quiting! {ret}")
        self.client.disconnect()
        quit(ret)

    def on_message(self, cl, userdata, msg):
        value = msg.payload.decode("utf-8")
        if msg.topic == f"/{self.args.device}/fw_upd" and value == '0':
            if self.exit_tmr is not None:
                self.exit_tmr.cancel();
            print("\r\nReseting device!")
            self.client.publish(f">{self.args.device}/fw_upd", '3')
            print(f"\r\nDone! in: { time.perf_counter() - self.elapsed:0.4f} seconds")
            self.exit_tmr = Timer(1.0,self.exit)
            self.exit_tmr.start()

        try:
            if msg.topic[1:] == f"{self.args.device}/fw_pkg":
                if self.exit_tmr is not None:
                    self.exit_tmr.cancel();
                
                val = json.loads(value)
                
                if 'chunk' in val:
                    val = val['chunk']
                    if len(self.raw_fw) > val:
                        if self.prevoius_idx == val:
                            self._err_cnt_inc()
                            print(f"\r\nRepeat sending {self.prevoius_idx} chunk")
                            time.sleep(2)
                        else:
                            self.error_cnt = 0

                        self.client.publish(f">{self.args.device}/fw_pkg", f'"{self.raw_fw[val]}"', qos=1)
                        self.print_progress(val, len(self.raw_fw)-1, prefix="Uploading: ")
                        self.prevoius_idx = val
                        self.exit_tmr = Timer(30.0,self.exit)
                        self.exit_tmr.start()
                        time.sleep(0.01)
                    else:
                        time.sleep(5)
                        print("\r\nStart upgrading..")
                        self.client.publish(f">{self.args.device}/fw_upd", '2', qos=1)
                        time.sleep(5)
                        self.client.publish(f">{self.args.device}/fw_upd", '3', qos=1)
                        self.exit_tmr = Timer(30.0,self.exit)
                        self.exit_tmr.start()
                elif 'error' in val:
                    print('\t Device return error: ', val['error'], ' Trying again', '.' * self.error_cnt)
                    self._err_cnt_inc()
                    self.client.publish(f">{self.args.device}/fw_pkg", f'"{self.raw_fw[self.prevoius_idx]}"', qos=1)
                    self.exit_tmr = Timer(30.0,self.exit)
                    self.exit_tmr.start()

        except ValueError:
            pass


def main(argv):
    args = Args(argv)
    if not os.path.exists(args.fw_file):
        print("File '" + args.fw_file + "' not exists \r\n")
        args.help()

    print("Use FW: " + args.fw_file)
    try:
        fw_root = xml_parser.parse(args.fw_file).getroot()
    except xml_parser.ParseError:
        print("Error parsing FW file")
        sys.exit(2)

    raw_fw = []

    try:
        fw_info(fw_root)
        for chunk in fw_root.find("chunks"):
            raw_fw.append(chunk.text)
    except AttributeError:
        print("Error parsing FW file")
        sys.exit(2)

    p = pyhlo(args,raw_fw)
    p.loop_forever()


if __name__ == "__main__":
    main(sys.argv[1:])
