# For testing mouse interaction with the curses library:with :e life. as target:

import curses
from curses import wrapper
import math
import time
import random

# Global items
CURSOR_VISIBILITY = 0
# CHARACTER = "\u2588"
CHARACTER = "."

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def frange(start, stop=None, step=None):
    # if set start=0.0 and step = 1.0 if not specified
    start = float(start)
    if stop == None:
        stop = start + 0.0
        start = 0.0
    if step == None:
        step = 1.0

    # print("start = ", start, "stop = ", stop, "step = ", step)

    count = 0
    while True:
        temp = float(start + count * step)
        if step > 0 and temp >= stop:
            break
        elif step < 0 and temp <= stop:
            break
        yield temp
        count += 1

def draw_line(x1, y1, x2, y2, win):
    # This function draws a line on the screen
    # between two pairs of cartesian coordinates

    # Compute x and y differences, used later
    # to determine the vector length and line slope
    y_diff = y1 - y2
    x_diff = x1 - x2

    # Check for divide by zero
    if x_diff != 0:
        vector_slope = y_diff / x_diff
    else:
        vector_slope = 1

    y_intercept = y1 - vector_slope * x1
    vector_length = math.ceil(math.sqrt(x_diff ** 2 + y_diff ** 2))

    win.addstr(0,0,f'{x1},{y1} to {x2},{y2}                ')
    win.addstr(1,0,f'vector length: {vector_length}        ')

    # Always draw horizontally from left to right
    if x2 > x1:
        x_line_start = x1
        x_line_end = x2
    else:
        x_line_start = x2
        x_line_end = x1

    for i in range(vector_length):
        # For the x position, make sure it is always multiplied by x_diff / vector_length
        # so that lines that are nearly or completely vertical can have all vertical characters drawn
        x_pos = constrain(x_line_start + (i * abs(x_diff) / vector_length), 0, term_width - 2)
        y_pos = constrain(int(vector_slope * x_pos + y_intercept), 0, term_height - 1)
        win.addstr(y_pos, int(x_pos), CHARACTER)
        # win.refresh()
        # time.sleep(0.0005)

def draw_circle(x, y, radius, filled, win):
    # This function draw a circle, either the outline of one
    # or filled.

    # Skip plotting the very first point, for some reason
    # it results in an artifact hanging off the rightmost
    # side of the circle
    first_round = True

    for theta in frange(0, 2 * math.pi, 0.01):
        x_end = x + radius * math.cos(theta)
        y_end = y + radius * math.sin(theta)
        if filled and not first_round:
            draw_line(x, y, x_end, y_end, win)
        elif not first_round:
            win.addstr(constrain(int(y_end), 0, term_height - 1), constrain(int(x_end), 0, term_width - 2), "*")
        first_round = False

def draw_polygon(polygon, win):
    # Function to take a polygon defined as a dict and
    # draw it on the screen.

    cartesian_x_vertice = []
    cartesian_y_vertice = []

    # Take the vertices expressed as polar coordinates and
    # convert them to cartesian, storing them in two arrays:
    # one array for x coordinates and another array for y
    # coordinates.
    for vertex in polygon["shape_vertices"]:
        x_cartesian = polygon["x_location"] + vertex["radius"] * math.cos(vertex["theta"])
        y_cartesian = polygon["y_location"] + vertex["radius"] * math.sin(vertex["theta"])
        cartesian_x_vertice.append(x_cartesian)
        cartesian_y_vertice.append(y_cartesian)

    # Draw lines between the two arrays of x and y cartesian
    # coordinates.
    for i in range(len(cartesian_x_vertice)):
        if i == len(cartesian_x_vertice) - 1:
            draw_line(cartesian_x_vertice[i], cartesian_y_vertice[i], cartesian_x_vertice[0], cartesian_y_vertice[0], win)
        else:
            draw_line(cartesian_x_vertice[i], cartesian_y_vertice[i], cartesian_x_vertice[i + 1], cartesian_y_vertice[i + 1], win)

def main(stdscr):

    key = None # For checking keypresses
    mouse_button_pressed = False

    curses.noecho()
    curses.curs_set(CURSOR_VISIBILITY)
    if curses.has_colors():
        curses.start_color()
    # curses.use_default_colors()
    # stdscr.clear()
    stdscr.nodelay(True)

    # Get screen dimensions
    global term_height, term_width
    term_height, term_width = stdscr.getmaxyx()

    # Set the aspect ration
    global aspect_ratio
    aspect_ratio = term_height / term_width
    
    # Create a new screen
    win = curses.newwin(term_height, term_width, 0, 0)
    curses.mousemask(-1) # Enable all features
    curses.mouseinterval(0) # Make the mouse fast

    # Create a polygon
    polygon = {
        "x_location": int(term_width / 2),
        "y_location": int(term_height / 2),
        "velocity": 0.05,
        "acceleration": 1,
        # Vertices are defined using polar coordinates
        # that are anchored to the x_location and
        # y_location variables.
        "shape_vertices": [
            {
                "radius": 12,
                "theta": math.pi / 4
            },
            {
                "radius": 12,
                "theta": math.pi * 3 / 4
            },
            {
                "radius": 12,
                "theta": math.pi *  3 / 2
            },
            {
                "radius": 1,
                "theta": math.pi * 7 / 4
            }

            # {
            #     "radius": math.sqrt(0**2 + abs(-2)**2),
            #     "theta": math.atan(2)
            # },
            # {
            #     "radius": math.sqrt(abs(-2)**2 + 5**2),
            #     "theta": math.atan(5/-2)
            # },
            # {
            #     "radius": math.sqrt(abs(-4)**2 + 5**2),
            #     "theta": math.atan(5/-4)
            # },
            # {
            #     "radius": math.sqrt(abs(-2)**2 + abs(-5)**2),
            #     "theta": math.atan(-5/-2)
            # },
            # {
            #     "radius": math.sqrt(2**2 + abs(-5)**2),
            #     "theta": math.atan(-5/2)
            # },
            # {
            #     "radius": math.sqrt(5**2 + 5**2),
            #     "theta": math.atan(5/5)
            # },
            # {
            #     "radius": math.sqrt(3**2 + 5**2),
            #     "theta": math.atan(5/3)
            # }
        ]
    }

    while True:
        # See if there's a keypress
        try:
            key = stdscr.get_wch()
        except:
            key = None # We are using nodelay, so set the key to None if nothing was pressed

        if key == 'q':
            return 0

        if key == 'w':
            for i in range(len(polygon["shape_vertices"])):
                polygon["shape_vertices"][i]["radius"] = polygon["shape_vertices"][i]["radius"] * 1.05

        if key == 'a':
            polygon["velocity"] = polygon["velocity"] * 1.05

        if key == 's':
            for i in range(len(polygon["shape_vertices"])):
                polygon["shape_vertices"][i]["radius"] = polygon["shape_vertices"][i]["radius"] * 0.95

        if key == 'd':
            polygon["velocity"] = polygon["velocity"] * 0.95


#         if key == curses.KEY_MOUSE:
#             win.addstr(1, 0, "mouse        ")
# 
#             _, x, y, _, bstate = curses.getmouse()
#             if bstate & curses.BUTTON1_PRESSED:
#                 mouse_button_pressed = True
#                 win.addstr(1, 0, "mouse button1  ")
#             elif bstate & curses.BUTTON1_RELEASED:
#                 mouse_button_pressed = False
#                 win.addstr(1, 0, "unmouse button1")
# 
#             win.addstr(y, x, "*")

        radius = random.randint(1, int(term_width / 8))
        x_start = random.randint(0, term_width - 2)
        y_start = random.randint(0, term_height - 1)

        # draw_circle(x_start, y_start, radius, random.getrandbits(1), win, term_height, term_width)
        # draw_circle(x_start, y_start, radius, random.getrandbits(1), win)
        draw_polygon(polygon, win)
        for i in range(len(polygon["shape_vertices"])):
            polygon["shape_vertices"][i]["theta"] = polygon["shape_vertices"][i]["theta"] + polygon["velocity"]
            polygon["velocity"] = polygon["velocity"] * polygon["acceleration"]
            # polygon["shape_vertices"][i]["radius"] = polygon["shape_vertices"][i]["radius"] * 1.01

        win.refresh()
        time.sleep(0.1)
        win.clear()

if __name__ == "__main__":
    wrapper(main)
