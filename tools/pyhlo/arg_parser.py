#!/usr/bin/python3

import sys
import getopt


class Args:
    def __init__(self, argv):
        self.fw_file = ""
        self.broker = ""
        self.device = ""

        if(len(argv) == 0):
            self.help()
        try:
            opts, args = getopt.getopt(
                argv, "hf:b:d:", ["help=", "fw=", "broker=", "device="])
        except getopt.GetoptError:
            self.help()
        for opt, arg in opts:
            if opt == "-h" or opt == "--help":
                self.help()
            if opt == "-f" or opt == "--fw":
                self.fw_file = arg
            if opt == "-b" or opt == "--broker":
                self.broker = arg
            if opt == "-d" or opt == "--device":
                if arg[0] == '/':
                    arg = arg[1:]

                self.device = arg

    def help(self):
        print("Use:")
        print("  * pyhlo.py -f <fw.uebf> -b <broker> -d <hub/device>" )
        print("  * pyhlo.py --fw <fw.uebf> --broker <broker>--device <hub/device>")
        print("Example:")
        print("  * pyhlo.py -f fw.uebf -b vegaiot.com -d 48:3f:da:7e:4c:2c/30567604" )
        print("  * pyhlo.py --fw fw.uebf --broker x.ks.ua --device 48:3f:da:7e:4c:2c/30567604")
        sys.exit(2)
