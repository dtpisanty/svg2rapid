# svg2rapid
SVG 2 RAPID contains scripts that convert vector files in SVG format to robot motion paths for ABB robots.

It has been tested on an IRB1600-10-1.45 robot using markers and ballpoint pens (many were broken in the process).

# Dependencies
* svgpathtools
* Numpy

# Usage
Currently all data must be hardcoded into svgConverter.py.
1. This script supposes that there is an existing world object created in Robot Studio with the right x,y,z coordinates and a tool.

1. Use the following guide to fill in the variables:
    __SVG_FILE__: Absolute path of the .svg file to convert
    __RESOLUTION__: Set the pixels per millimeter (metric only for now)
    __UNITS__: Defines the units of the input file (either px or mm)
    __TRAVEL_HEIGHT__: Tool centre-point height for travel
    __DRAW_HEIGHT__: Tool centre-point height for drawing
    __WOBJ__: World object name (usually defined in robot studio)
    __TOOL__: Tool name (usually defined in robot studio)
    __V_TRAVEL__: Travel speed
    __V_DRAW__: Drawing speed
    __BEZIER_RESOLUTION__: Curves must be aproximated with straight segments. How many segments should be used? (a small number will produce jagged lines, a large one will produce very short movements)

# Roadmap
1. Turn script into a command-line interface
1. Make the line width from the SVG file drive the robot's 6th axis rotation
1. World object and end-arm tooling creation from within the script.

# Support
Not using Robot Studio? Don't know what to do? Send me an email: dtrujillop@centro.edu.mx or diego@trujillodiego.com

# Credits
This work was created by Diego Trujillo-Pisanty within STEAM Lab at CENTRO.

