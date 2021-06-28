import time
from datetime import datetime
import math
from rpi_ws281x import Color
import logging
import signal
from threading import Event
from ledstrip import LedStrip
import random
import pandas as pd

class Wordclock():

    def __init__(
        self,
        ledBrightness = 100,     # Set to 0 for darkest and 255 for brightest
        ledColor = Color(255, 65, 0), # rgb
        roundTimeDown = True   # True to round down minutes to last 5 minutes - False to round up to the next 5 minutes
    ):
        self._ledStrip = LedStrip(ledBrightness=ledBrightness)
        self._roundTimeDown = roundTimeDown
        self._oldNow = None
        self._oldHour = None
        self._oldMinute = None
        self.ledColor = ledColor
        self._previousIndices = None

        if roundTimeDown:
            self.rounder = math.floor
        else:
            self.rounder = math.ceil

        # LED INDICES
        self._defaultLeds = list(range(9,11)) + list(range(5, 8)) # es + ist
        self._clockLeds = list(range(119, 122))    # uhr
        self._halfLeds = list(range(55, 59))      # halb
        self._quarterLeds = list(range(23, 30))   # viertel
        self._shortlyLeds = list(range(30, 34))   # viertel
        self._beforeLeds = list(range(40, 43))    # vor
        self._afterLeds = list(range(43, 47))     # nach
        self._fiveMinLeds = list(range(35, 39))    # fünf (1)
        self._tenMinLeds = list(range(11, 15))    # zehn (1)
        self._twentyMinLeds = list(range(16, 23)) # zwanzig
        self._hourLeds = {
            11: list(range(51, 54)),    # elf
            5: list(range(48, 52)),     # fünf (2)
            1: list(range(59, 63)),     # eins
            2: list(range(65, 69)),     # zwei
            3: list(range(78, 82)),     # drei (2)
            4: list(range(72, 76)),     # vier
            6: list(range(83, 88)),     # sechs
            8: list(range(89, 93)),     # acht
            7: list(range(100, 106)),   # sieben
            12: list(range(95, 100)),   # zwölf
            0: list(range(95, 100)),    # zwölf also used for 0
            10: list(range(107, 111)),  # zehn (2)
            9: list(range(110, 114)),   # neun
        }
        self._minuteToLeds = {
            0: self._clockLeds,
            1: self._shortlyLeds + self._afterLeds,
            2: self._shortlyLeds + self._afterLeds,
            3: self._shortlyLeds + self._afterLeds,
            4: self._shortlyLeds + self._afterLeds,
            5: self._fiveMinLeds + self._afterLeds,
            6: self._tenMinLeds + self._afterLeds,
            7: self._tenMinLeds + self._afterLeds,
            8: self._tenMinLeds + self._afterLeds,
            9: self._tenMinLeds + self._afterLeds,
            10: self._tenMinLeds + self._afterLeds,
            11: self._quarterLeds + self._afterLeds,
            12: self._quarterLeds + self._afterLeds,
            13: self._quarterLeds + self._afterLeds,
            14: self._quarterLeds + self._afterLeds,
            15: self._quarterLeds + self._afterLeds,
            16: self._twentyMinLeds + self._afterLeds,
            17: self._twentyMinLeds + self._afterLeds,
            18: self._twentyMinLeds + self._afterLeds,
            19: self._twentyMinLeds + self._afterLeds,
            20: self._twentyMinLeds + self._afterLeds,
            21: self._tenMinLeds + self._beforeLeds + self._halfLeds,
            22: self._tenMinLeds + self._beforeLeds + self._halfLeds,
            23: self._tenMinLeds + self._beforeLeds + self._halfLeds,
            24: self._tenMinLeds + self._beforeLeds + self._halfLeds,
            25: self._fiveMinLeds + self._beforeLeds + self._halfLeds,
            26: self._shortlyLeds + self._beforeLeds + self._halfLeds,
            27: self._shortlyLeds + self._beforeLeds + self._halfLeds,
            28: self._shortlyLeds + self._beforeLeds + self._halfLeds,
            29: self._halfLeds,
            30: self._halfLeds,
            31: self._shortlyLeds + self._afterLeds + self._halfLeds,
            32: self._shortlyLeds + self._afterLeds + self._halfLeds,
            33: self._shortlyLeds + self._afterLeds + self._halfLeds,
            34: self._shortlyLeds + self._afterLeds + self._halfLeds,
            35: self._fiveMinLeds + self._afterLeds + self._halfLeds,
            36: self._twentyMinLeds + self._beforeLeds,
            37: self._twentyMinLeds + self._beforeLeds,
            38: self._twentyMinLeds + self._beforeLeds,
            39: self._twentyMinLeds + self._beforeLeds,
            40: self._twentyMinLeds + self._beforeLeds,
            41: self._quarterLeds + self._beforeLeds,
            42: self._quarterLeds + self._beforeLeds,
            43: self._quarterLeds + self._beforeLeds,
            44: self._quarterLeds + self._beforeLeds,
            45: self._quarterLeds + self._beforeLeds,
            46: self._tenMinLeds + self._beforeLeds,
            47: self._tenMinLeds + self._beforeLeds,
            48: self._tenMinLeds + self._beforeLeds,
            49: self._tenMinLeds + self._beforeLeds,
            50: self._tenMinLeds + self._beforeLeds,
            51: self._fiveMinLeds + self._beforeLeds,
            52: self._fiveMinLeds + self._beforeLeds,
            53: self._fiveMinLeds + self._beforeLeds,
            54: self._fiveMinLeds + self._beforeLeds,
            55: self._fiveMinLeds + self._beforeLeds,
            56: self._shortlyLeds + self._beforeLeds,
            57: self._shortlyLeds + self._beforeLeds,
            58: self._shortlyLeds + self._beforeLeds,
            59: self._shortlyLeds + self._beforeLeds,
        }

        self._exitFlag = self._setupExitHandler()

    def _setupExitHandler(self):
        for sig in ('TERM', 'HUP', 'INT'):
            signal.signal(getattr(signal, 'SIG'+sig), self.quit)
        return Event()

    def quit(self, signo, _frame):
        logging.info("Interrupted by {0}, shutting down".format(signo))
        self._exitFlag.set()

    def getNextUpdateTime(self):
        oldRoundedNow = datetime(self._now.year, self._now.month, self._now.day, self._hour, self._minute)
        if (self._roundTimeDown):
            return oldRoundedNow + datetime.timedelta(minutes=1)
        return oldRoundedNow

    def getRoundedTime(self, now=None):
        #if (now is None):
        self._now = datetime.now()

        hour,min,sec = str(datetime.now().time()).split(":")
        self._hour = int(hour)
        self._minute = int(min)

    def _convertTimeToLedIndices(self):
        ledIndices = list(self._defaultLeds) # copy the list
        ledIndices += self._convertHourToLedIndices()
        ledIndices += self._convertMinuteToLedIndices()
        return ledIndices

    def _convertHourToLedIndices(self):
        hour = self._hour

        if self._minute > 20:
            hour += 1

        if hour > 12:
            hour -= 12

        if hour == 1 and self._minute == 0:
            # special case: print "Ein Uhr" instead of "Eins Uhr"
            return self._hourLeds[hour][1:]
        else:
            return self._hourLeds[hour]

    def _convertMinuteToLedIndices(self):
        return self._minuteToLeds[self._minute]

    def runClock(self):
        while not self._exitFlag.is_set():
            self.getRoundedTime()

            if self._minute > 59:
                self._minute = 0
                self._hour = self._hour +1

            #logging.info("Time: {0} - Rounded: {1}:{2}".format(self._now, self._hour, self._minute))

            ledIndices = self._convertTimeToLedIndices()
            #logging.debug("LEDs ({0}): {1}".format(len(ledIndices),ledIndices))
            self.ledColor = Color(random.randint(50, 255),random.randint(50, 255),random.randint(50, 255))

            if self._previousIndices is not None:
                self._ledStrip.clear(self._previousIndices, 10)
            #else:
             #in case something went wrong: clear the whole thing
            self._ledStrip.clear()


            self._ledStrip.colorWipe(self.ledColor, ledIndices, 10)
            self._previousIndices = ledIndices


            delay = (self.getNextUpdateTime() - self._now).total_seconds()+60
            if delay < 1:
                delay = 10
            print("----")
            print(delay)
            print(self._now)
            self._exitFlag.wait(delay)
        self.clear()

    def clear(self):
        if self._exitFlag is not None:
            self._exitFlag.set()
        if self._ledStrip is not None:
            self._ledStrip.clear()

if __name__ == '__main__':
    clock = None
    try:
        logging.basicConfig(level=logging.DEBUG, filename='wordclock.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        clock = Wordclock(230, Color(255, 65, 0), False)
        clock.runClock()
    except Exception:
        logging.exception("Unhandled Exception occured.")
        if clock is not None:
            clock.clear()
