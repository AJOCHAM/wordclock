"""
This file includes code copied and modified from:
https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/examples/strandtest.py
which is published under BSD 2-Clause License:
https://github.com/rpi-ws281x/rpi-ws281x-python/blob/master/LICENSE

BSD 2-Clause License

Copyright (c) 2018, Pimoroni Ltd
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import time
from rpi_ws281x import Adafruit_NeoPixel, Color

class LedStrip():
    def __init__(
        self,
        ledCount = 110,      # Number of LED pixels.
        ledPin = 18,      # GPIO pin connected to the pixels (18 uses PWM, 10 uses SPI /dev/spidev0.0).
        ledFreqHz = 800000,  # LED signal frequency in hertz (usually 800khz)
        ledDma = 10,      # DMA channel to use for generating signal (try 10)
        ledBrightness = 255,     # Set to 0 for darkest and 255 for brightest
        ledInvert = False,   # True to invert the signal (when using NPN transistor level shift)
        ledChannel = 0,       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        clearStrip = True
    ):
        self._ledCount = ledCount
        self._ledPin = ledPin
        self._ledFreqHz = ledFreqHz
        self._ledDma = ledDma
        self._ledBrightness = ledBrightness
        self._ledInvert = ledInvert
        self._ledChannel = ledChannel
        
        self.strip = None
        self.strip = self._setup()

        if clearStrip:
            self.clear()

    def _setup(self):
        """Setups the hardware strip"""
        if self.strip is None:
            strip = Adafruit_NeoPixel(self._ledCount, self._ledPin, self._ledFreqHz, self._ledDma, self._ledInvert, self._ledBrightness, self._ledChannel)
            strip.begin()
            return strip

    def clear(self, delay = 0):
        """Turns off the whole strip"""
        self.colorWipe(Color(0,0,0), delay)

    def clear(self, indices, delay = 0):
        """Turns off the specified LEDs"""
        self.colorWipe(Color(0,0,0), indices, wait_ms)

    def colorWipe(self, color, indices, delay=0):
        """Turns on all leds defined in 'indices' with color specified a pixel at a time."""
        for i in indices:
            self.strip.setPixelColor(i, color)
            if delay != 0:
                self.strip.show()

            time.sleep(delay/1000.0)

        if delay == 0:
            self.strip.show()

    def colorWipe(self, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        self.colorWipe(color, range(self.strip.numPixels()), wait_ms)

    def theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, self.wheel((i+j) % 255))
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)
