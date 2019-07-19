#!/usr/bin/env python
# -*- coding: utf-8 -*-


from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
import inkyphat

colour = "red"
ink = InkyPHAT(colour)
ink.set_border(ink.BLACK)

print("w:" + str(ink.WIDTH) + " h:" + str(ink.HEIGHT))

# Create a new canvas to draw on
img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the FredokaOne font
font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 22)

# Draw lines to frame the weather data
draw.rectangle([(0, 0), (ink.WIDTH, ink.HEIGHT)], fill=ink.WHITE)

draw.text((2, 2), "Hello", ink.BLACK, font=font)
draw.text((0, 0), "Hello", ink.RED, font=font)

draw.text((2, 32), "World !", ink.BLACK, font=font)
draw.text((0, 30), "World !", ink.RED, font=font)


# Display the weather data on Inky pHAT
ink.set_image(img)
ink.show()
