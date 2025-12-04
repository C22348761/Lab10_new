import array, time
from machine import Pin
import rp2

# WS2812 PIO program for precise timing control
# Timing: T1=2, T2=5, T3=3 cycles (WS2812 requires ~800kHz bit rate)
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2  # Low time for '0' bit
    T2 = 5  # High time for '0' bit / total time for '1' bit
    T3 = 3  # Low time for '1' bit
    wrap_target()
    label("bitloop")
    out(x, 1) .side(0) [T3 - 1]  # Output bit, set pin low
    jmp(not_x, "do_zero") .side(1) [T1 - 1]  # If bit is 0, jump; else set pin high
    jmp("bitloop") .side(1) [T2 - 1]  # Continue loop, keep pin high
    label("do_zero")
    nop() .side(0) [T2 - 1]  # Keep pin low for '0' bit duration
    wrap()
class WS2812():        
    def __init__(self, pin_num, led_count, brightness = 0.5):
        """Initialize WS2812 LED strip.
        Args:
            pin_num: GPIO pin number for data line
            led_count: Number of LEDs in strip
            brightness: Brightness level (0.0-1.0)
        """
        self.Pin = Pin
        self.led_count = led_count
        self.brightness = brightness
        # State machine at 8MHz provides ~800kHz bit rate for WS2812
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(pin_num))
        self.sm.active(1)
        self.ar = array.array("I", [0 for _ in range(led_count)])  # Color buffer
        
    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
        time.sleep_ms(10)

    def pixels_set(self, i, color):
        """Set pixel color. Color format: (R, G, B) tuple.
        Internal format: GRB (WS2812 expects green first).
        """
        self.ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]  # GRB encoding

    def pixels_fill(self, color):
        for i in range(len(self.ar)):
            self.pixels_set(i, color)

    def color_chase(self,color, wait):
        for i in range(self.led_count):
            self.pixels_set(i, color)
            time.sleep(wait)
            self.pixels_show()
        time.sleep(0.2)
    def wheel(self, pos):
        """Generate color wheel value (0-255).
        Returns RGB tuple transitioning: red -> green -> blue -> red.
        """
        if pos < 0 or pos > 255:
            return (0, 0, 0)
        if pos < 85:  # Red to green
            return (255 - pos * 3, pos * 3, 0)
        if pos < 170:  # Green to blue
            pos -= 85
            return (0, 255 - pos * 3, pos * 3)
        pos -= 170  # Blue to red
        return (pos * 3, 0, 255 - pos * 3)


    def rainbow_cycle(self, wait):
        for j in range(255):
            for i in range(self.led_count):
                rc_index = (i * 256 // self.led_count) + j
                self.pixels_set(i, self.wheel(rc_index & 255))
            self.pixels_show()
            time.sleep(wait)

