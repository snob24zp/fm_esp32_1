#!/usr/bin/python3


import os
import base64
import time
import random
import unittest
import xmlrunner

from test_tpl import test_tpl

class events_test(test_tpl):

    def setUp(self):
        super().setUp()
        self.topic = None
        self.value = None
        self.collected_evts = []

    
    def get_events(self, _from, _to):
        self.logger.warning(f'Get events from {_from} to: {_to}')
        evts = []
        found_end = False

        def on_evts(topic, msg):
            nonlocal found_end, evts
            found_end = msg == {}
            if not found_end:
                evts.extend(msg)

        self.subscribe_device('events/9', on_evts)
        self.publish_device('events/9', f'{_from};{_to}')
        self.wait_condition(lambda: found_end, 60)
        self.logger.info(f'events: {evts}')
        self.assertTrue(len(evts) > 0)
        skip = None
        for k,v in enumerate(evts):
            for _, ov in enumerate(self.collected_evts):
                if v['v'] == ov:
                    skip = k
                    break
            if skip is not None:
                break
        
        evts = evts[skip:]
        for k,v in enumerate(evts):
            self.assertTrue(v['v'] == self.collected_evts[k])


    def collect_events(self):
        count = 15
        pre_time = time.time()
        while count:
            if time.time() > (pre_time + 5):
                evt = {'tm': int(time.time() * 1000),
                       'rnd_a': random.randint(0, 2**30),
                       'rnd_data': base64.b64encode(random.randbytes(random.randint(0, 32))).decode()
                       }
                self.collected_evts.append(evt)
                self._device.set_reg(9, evt)
                pre_time = time.time()
                count -= 1

    def test(self):
        start_tm = int(time.time() * 1000)
        self.collect_events()
        stop_tm = int(time.time() * 1000)
        self.get_events(start_tm, stop_tm)


if __name__ == "__main__":
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output=os.path.join(os.getcwd(), "out/tests")))
