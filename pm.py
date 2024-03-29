import curses
from curses import wrapper
import math
import time

# Global items
CURSOR_VISIBILITY = 0
# CHARACTER = "\u2588"
CHARACTER = "."

# This is the projection matrix we will use
# to convert a 3d point to a 2d point.
# Since the last row is all zeroes it can
# be dropped, but it is left here for clarity
projection_matrix = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 0]
]

# Represent a 3d pyramid using
# coordinates in the form of
# x, y, and z
# These points are normalized.
polygon = [
    [-1, -1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, -1, -1],
    [0, 1, 0]
]

# Constrain all values, used to ensure lines stay within
# the size of the terminal.
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

# This takes the place of doing the math for the
# projection matrix, since that's a lot of loops
# and multiplying by zero when it is much more simply
# done here.
def mul_projection(position_matrix):
    row1 = position_matrix[0]
    row2 = position_matrix[1]
    row3 = 0

    return [row1, row2, row3]

def x_rotation(position_matrix, angle):
    # Compute the dot product of an
    # 3,1 x, y, z matrix against a
    # 3,3 x rotation matrix
    # [ 1, 0,          0 ]
    # [ 0, cos(theta), -sin(theta) ]
    # [ 0, sin(theta), cos(theta)  ]
    # Matrix multiplication is not done since
    # it is stated much more simply using this formula and
    # we do not need to worry about N x N matrix math
    row1 = position_matrix[0]
    row2 = (position_matrix[1] * math.cos(angle)) + (position_matrix[2] * -math.sin(angle))
    row3 = (position_matrix[1] * math.sin(angle)) + (position_matrix[2] * math.cos(angle))

    return [row1, row2, row3]

def y_rotation(position_matrix, angle):
    # Compute the dot product of an
    # 3,1 x, y, z matrix against a
    # 3,3 y rotation matrix
    # [ cos(theta),  0, sin(theta) ]
    # [ 0,           1, 0 ]
    # [ -sin(theta), 0, sin(theta) ]
    row1 = (position_matrix[0] * math.cos(angle)) + (position_matrix[2] * math.sin(angle))
    row2 = position_matrix[1]
    row3 = (position_matrix[0] * -math.sin(angle)) + (position_matrix[2] * math.sin(angle))

    return [row1, row2, row3]

def z_rotation(position_matrix, angle):
    # Compute the dot product of an
    # 3,1 x, y, z matrix against a
    # 3,3 z rotation matrix
    # [ cos(theta), -sin(theta), 0 ]
    # [ sin(theta), cos(theta),  0 ]
    # [ 0,          0,           1 ]
    row1 = (position_matrix[0] * math.cos(angle)) + (position_matrix[1] * -math.sin(angle))
    row2 = (position_matrix[0] * math.sin(angle)) + (position_matrix[1] * math.cos(angle))
    row3 = position_matrix[2]

    return [row1, row2, row3]

def draw_point(x, y, win):
    # Draw points on the screen.
    win.addstr(y, x, CHARACTER)

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

def main(stdscr):
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
    
    origin_x = int(term_width / 2)
    origin_y = int(term_height / 2)
    scale = 25
    x_angle = 0
    y_angle = 0
    z_angle = 0
    x_angle_velocity = 0.1
    y_angle_velocity = 0.1
    z_angle_velocity = 0.1
    scale_velocity = 1

    # Create a new screen
    win = curses.newwin(term_height, term_width, 0, 0)

    # Set default keypress value
    key = None

    while True:
        # See if there's a keypres
        try:
            key = stdscr.get_wch()
        except:
            key = None # We are using nodelay, so set the key to None if nothing was pressed

        if key == 'q':
            return 0

        if key == 'w':
            x_angle += x_angle_velocity
        if key == 's':
            x_angle -= x_angle_velocity
        if key == 'a':
            y_angle -= y_angle_velocity
        if key == 'd':
            y_angle += y_angle_velocity
        if key == 'e':
            z_angle += z_angle_velocity
        if key == 'c':
            z_angle -= z_angle_velocity
        if key == '=':
            scale += scale_velocity
        if key == '-':
            scale -= scale_velocity

        i = 0
        cartesian_polygon = []

        for point_3d in polygon:

            # Rotate around the 3 axes
            x_rotated = x_rotation(point_3d, x_angle)
            y_rotated = y_rotation(x_rotated, y_angle)
            z_rotated = z_rotation(y_rotated, z_angle)

            # Convert the 3d point to a 2d point using the projection matrix
            # point_2d = mul_projection(point_3d)
            point_2d = mul_projection(z_rotated)

            # Compute the x value after rotation
            # for aspect ratio
            x = origin_x + int(point_2d[0] * scale)

            # Compute the y value after rotation
            #
            # Note that in curses an increasing Y value means going down,
            # and in cartesian coordinates an increasing Y value means going up,
            # so we multiply Y times -1 to get the desired effect.
            y = int(origin_y + point_2d[1] * scale * -1 * aspect_ratio)
            # y = int(origin_y + point[1] * scale * -1 * aspect_ratio)

            # Draw the point on the screen
            # draw_point(x, y, win)

            # Increase the angles
            # x_angle += x_angle_velocity
            # y_angle += y_angle_velocity
            # z_angle += z_angle_velocity

            # Place these coordinates in a new array so that we can draw edges
            cartesian_polygon.append([x, y])
            i += 1

        # Draw the edges
        draw_line(cartesian_polygon[0][0], cartesian_polygon[0][1], cartesian_polygon[1][0], cartesian_polygon[1][1], win)
        draw_line(cartesian_polygon[1][0], cartesian_polygon[1][1], cartesian_polygon[2][0], cartesian_polygon[2][1], win)
        draw_line(cartesian_polygon[2][0], cartesian_polygon[2][1], cartesian_polygon[3][0], cartesian_polygon[3][1], win)
        draw_line(cartesian_polygon[3][0], cartesian_polygon[3][1], cartesian_polygon[0][0], cartesian_polygon[0][1], win)

        draw_line(cartesian_polygon[0][0], cartesian_polygon[0][1], cartesian_polygon[4][0], cartesian_polygon[4][1], win)
        draw_line(cartesian_polygon[1][0], cartesian_polygon[1][1], cartesian_polygon[4][0], cartesian_polygon[4][1], win)
        draw_line(cartesian_polygon[2][0], cartesian_polygon[2][1], cartesian_polygon[4][0], cartesian_polygon[4][1], win)
        draw_line(cartesian_polygon[3][0], cartesian_polygon[3][1], cartesian_polygon[4][0], cartesian_polygon[4][1], win)

        win.refresh()
        time.sleep(0.1)
        win.clear()

if __name__ == "__main__":
    wrapper(main)
