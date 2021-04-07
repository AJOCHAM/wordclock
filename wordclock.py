import time
import datetime
import math
from rpi_ws281x import Color
import logging
import signal
from threading import Event
from ledstrip import LedStrip

class Wordclock():

    def __init__(
        self,
        ledBrightness = 1,     # Set to 0 for darkest and 255 for brightest
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
        self._beforeLeds = list(range(40, 43))    # vor
        self._afterLeds = list(range(43, 47))     # nach
        self._fiveMinLeds = list(range(30, 34))    # fünf (1)
        self._tenMinLeds = list(range(11, 15))    # zehn (1)
        self._twentyMinLeds = list(range(16, 23)) # zwanzig
        self._hourLeds = {
            11: list(range(49, 52)),    # elf
            5: list(range(51, 55)),     # fünf (2)
            1: list(range(62, 66)),     # eins 
            2: list(range(55, 59)),     # zwei
            3: list(range(66, 70)),     # drei (2)
            4: list(range(73, 77)),     # vier
            6: list(range(83, 88)),     # sechs
            8: list(range(77, 81)),     # acht 
            7: list(range(88, 94)),     # sieben
            12: list(range(94, 99)),    # zwölf
            0: list(range(94, 99)),     # zwölf also used for 0
            10: list(range(106, 110)),  # zehn (2)
            9: list(range(103, 107)),   # neun
        }
        self._minuteToLeds = {
            0: self._clockLeds,
            5: self._fiveMinLeds + self._afterLeds,
            10: self._tenMinLeds + self._afterLeds,
            15: self._quarterLeds + self._afterLeds,
            20: self._twentyMinLeds + self._afterLeds,
            25: self._fiveMinLeds + self._beforeLeds + self._halfLeds,
            30: self._halfLeds,
            35: self._fiveMinLeds + self._afterLeds + self._halfLeds,
            40: self._twentyMinLeds + self._beforeLeds,
            45: self._quarterLeds + self._beforeLeds,
            50: self._tenMinLeds + self._beforeLeds,
            55: self._fiveMinLeds + self._beforeLeds
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
        oldRoundedNow = datetime.datetime(self._now.year, self._now.month, self._now.day, self._hour, self._minute)
        if (self._roundTimeDown):
            return oldRoundedNow + datetime.timedelta(minutes=5)
        return oldRoundedNow
    
    def getRoundedTime(self, now=None):
        if (now is None):
            now = datetime.datetime.now()
        self._now = now
        self._hour = now.hour
        self._minute = self.rounder(now.minute / 5) * 5

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
            logging.info("Time: {0} - Rounded: {1}:{2}".format(self._now, self._hour, self._minute))
            ledIndices = self._convertTimeToLedIndices()
            logging.debug("LEDs ({0}): {1}".format(len(ledIndices),ledIndices))

            if self._previousIndices is not None:
                self._ledStrip.clear(self._previousIndices, 10)

            # in case something went wrong: clear the whole thing
            self._ledStrip.clear()
            self._ledStrip.colorWipe(self.ledColor, ledIndices, 10)
            self._previousIndices = ledIndices

            delay = (self.getNextUpdateTime() - datetime.datetime.now()).total_seconds()
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
        clock = Wordclock(50, Color(255, 65, 0),True)
        clock.runClock()
    except Exception:
        logging.exception("Unhandled Exception occured.")
        if clock is not None:
            clock.clear()


