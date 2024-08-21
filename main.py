import math
import re

import ezdxf
from PIL import Image, ImageOps
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from matplotlib import pyplot as plt

# constant
box_width = 40  # in cm
box_height = 20  # in cm
corner_radius = 1  # 1 cm radius for the rounded corners
pico_w = 2.2
pico_h = 5.2
switch_width = 1.4
oled_height = 1.9
oled_width = 3.5
pico_y_from_top = .38

def draw_oled(msp, box_width, box_height, rect_width, rect_height):
    """
    Draws a rectangle centered within a box.

    Args:
    - msp: The model space where the rectangle is drawn.
    - box_width: The width of the surrounding box.
    - box_height: The height of the surrounding box.
    - rect_width: The width of the rectangle to be drawn.
    - rect_height: The height of the rectangle to be drawn.
    """
    # Calculate the lower left corner (start point) of the rectangle
    start_x = (box_width - rect_width) / 2
    start_y = (box_height - rect_height) / 2

    # Calculate the remaining corners
    points = [
        (start_x, start_y),  # Bottom-left
        (start_x + rect_width, start_y),  # Bottom-right
        (start_x + rect_width, start_y + rect_height),  # Top-right
        (start_x, start_y + rect_height),  # Top-left
        (start_x, start_y)  # Closing the loop back to bottom-left
    ]

    # Draw the rectangle
    msp.add_lwpolyline(points)
    
def draw_oled_bottom(msp, oled_bottom_height):
    start_x = box_width / 2 - oled_width / 2
    start_y = box_height / 2 - oled_height / 2 - oled_bottom_height
    points = [
        (start_x, start_y),  # Bottom-left
        (start_x + oled_width, start_y),  # Bottom-right
        (start_x + oled_width, start_y + oled_bottom_height),  # Top-right
        (start_x, start_y + oled_bottom_height),  # Top-left
        (start_x, start_y)  # Closing the loop back to bottom-left
    ]
    msp.add_lwpolyline(points)
    
def draw_oled_top(msp, oled_top_height):
    start_x = box_width / 2 - oled_width / 2
    start_y = box_height / 2 + oled_height / 2
    points = [
        (start_x, start_y),  # Bottom-left
        (start_x + oled_width, start_y),  # Bottom-right
        (start_x + oled_width, start_y + oled_top_height),  # Top-right
        (start_x, start_y + oled_top_height),  # Top-left
        (start_x, start_y)  # Closing the loop back to bottom-left
    ]
    msp.add_lwpolyline(points)
    
def draw_oled_wire(msp):
    wire_height = .3
    wire_width = 1.4
    start_x = box_width / 2- wire_width / 2
    start_y = box_height / 2 + oled_height / 2 + .1

    points = [
        (start_x, start_y),  # Bottom-left
        (start_x + wire_width, start_y),  # Bottom-right
        (start_x + wire_width, start_y + wire_height),  # Top-right
        (start_x, start_y + wire_height),  # Top-left
        (start_x, start_y)  # Closing the loop back to bottom-left
    ]

    # Draw the rectangle
    msp.add_lwpolyline(points)

def draw_usb(msp, start_x, start_y, rect_width, rect_height, y_from_top):
    """
    Draws a rectangle centered horizontally within a box and aligned to the top edge.

    Args:
    - msp: The model space where the rectangle is drawn.
    - box_width: The width of the surrounding box.
    - box_height: The height of the surrounding box.
    - rect_width: The width of the rectangle to be drawn.
    - rect_height: The height of the rectangle to be drawn.
    """
    # The y coordinate will be at the top edge of the box (so no vertical offset)
    start_x = start_x - rect_width / 2
    start_y = start_y - rect_height - y_from_top

    # Calculate the remaining corners
    points = [
        (start_x, start_y),  # Bottom-left
        (start_x + rect_width, start_y),  # Bottom-right
        (start_x + rect_width, start_y + rect_height),  # Top-right
        (start_x, start_y + rect_height),  # Top-left
        (start_x, start_y)  # Closing the loop back to bottom-left
    ]

    # Draw the rectangle
    msp.add_lwpolyline(points)

def add_rounded_square(msp, box_width, box_height, corner_radius, start_point = (0, 0)):
    """
    Draw a rounded rectangle (square) using lines and arcs.

    Args:
    - msp: The model space where the rectangle is drawn.
    - start_point: The starting point (x, y) for the rounded rectangle.
    - box_width: Width of the rectangle.
    - box_height: Height of the rectangle.
    - corner_radius: Radius of the rounded corners.
    """
    x0, y0 = start_point  # Unpack the start point coordinates

    # Calculate corner points relative to the start point
    points = [
        (x0 + corner_radius, y0),  # Start at bottom left (but offset by the corner radius)
        (x0 + box_width - corner_radius, y0),
        (x0 + box_width, y0 + corner_radius),
        (x0 + box_width, y0 + box_height - corner_radius),
        (x0 + box_width - corner_radius, y0 + box_height),
        (x0 + corner_radius, y0 + box_height),
        (x0, y0 + box_height - corner_radius),
        (x0, y0 + corner_radius)
    ]

    # Draw lines and arcs
    msp.add_lwpolyline([points[0], points[1]])  # Bottom line
    msp.add_arc((x0 + box_width - corner_radius, y0 + corner_radius), corner_radius, 270, 360)  # Bottom-right corner
    msp.add_lwpolyline([points[2], points[3]])  # Right line
    msp.add_arc((x0 + box_width - corner_radius, y0 + box_height - corner_radius), corner_radius, 0, 90)  # Top-right corner
    msp.add_lwpolyline([points[4], points[5]])  # Top line
    msp.add_arc((x0 + corner_radius, y0 + box_height - corner_radius), corner_radius, 90, 180)  # Top-left corner
    msp.add_lwpolyline([points[6], points[7]])  # Left line
    msp.add_arc((x0 + corner_radius, y0 + corner_radius), corner_radius, 180, 270)  # Bottom-left corner
    
def draw_usb_connector(msp):
    # Initialize list of points for polyline
    points = [
        (19.5, 20),
        (19.5, box_height - pico_y_from_top),
        (20.5, box_height - pico_y_from_top),
        (20.5, 20),
    ]
    
    # Draw the polyline
    msp.add_lwpolyline(points)


def add_rounded_square_with_small_squares(msp, box_width, box_height, corner_radius, small_squares):
    """
    Draw a rounded rectangle (square) using lines and arcs, and place small squares on top, adjusting for overlap.

    Args:
    - msp: The model space where the rectangle is drawn.
    - box_width: Width of the rectangle.
    - box_height: Height of the rectangle.
    - corner_radius: Radius of the rounded corners.
    - small_squares: Array of tuples (width, height, center_x) for small squares to be drawn on top.
    """
    # Calculate corner points
    # Calculate corner points
    points = [
        (corner_radius, 0),  # Start at bottom left (but offset by the corner radius)
        (box_width - corner_radius, 0),
        (box_width, corner_radius),
        (box_width, box_height - corner_radius),
        (box_width - corner_radius, box_height),
        (corner_radius, box_height),
        (0, box_height - corner_radius),
        (0, corner_radius)
    ]

    # Draw lines and arcs
    msp.add_lwpolyline([points[0], points[1]])  # Bottom line
    msp.add_arc((box_width - corner_radius, corner_radius), corner_radius, 270, 360)  # Bottom-right corner
    msp.add_lwpolyline([points[2], points[3]])  # Right line
    msp.add_arc((box_width - corner_radius, box_height - corner_radius), corner_radius, 0, 90)  # Top-right corner
    msp.add_lwpolyline([points[4], points[5]])  # Top line
    msp.add_arc((corner_radius, box_height - corner_radius), corner_radius, 90, 180)  # Top-left corner
    msp.add_lwpolyline([points[6], points[7]])  # Left line
    msp.add_arc((corner_radius, corner_radius), corner_radius, 180, 270)  # Bottom-left corner


def reverse_x(x, width):
    return width - x

def cal_equiliteral_triangle(xHP, yHP, xHK, yHK):
    # Since DI, HP, and HK form an equilateral triangle, the distance from DI to HP and DI to HK is the same as d_HP_HK
    # Distance between HP and HK
    d_HP_HK = math.sqrt((xHP - xHK) ** 2 + (yHP - yHK) ** 2)
    # Using the midpoint formula and properties of an equilateral triangle
    x_mid = (xHP + xHK) / 2
    y_mid = (yHP + yHK) / 2
    # Calculate the distance from the midpoint to the center of DI
    height = math.sqrt(d_HP_HK ** 2 - ((d_HP_HK / 2) ** 2))
    # Calculate the coordinates of DI
    xDI = x_mid - height * (yHP - yHK) / d_HP_HK
    yDI = y_mid + height * (xHP - xHK) / d_HP_HK
    # Calculate the coordinates of DI on the right side
    xDI_right = x_mid + height * (yHP - yHK) / d_HP_HK
    yDI_right = y_mid - height * (xHP - xHK) / d_HP_HK

    return xDI_right, yDI_right, xDI, yDI

def get_big_circle_points():
    button_radius = 1.315
    # Calculate the position of the second circle
    distance_between_centers = 2.8  # 28 mm = 2.8 cm
    angle_degrees = 20  # Angle in degrees
    angle_radians = math.radians(angle_degrees)  # Convert angle to radians
    # Define names for each circle
    names = [
        'LP', 'MP', 'HP', 'LK', 'MK', 'HK', 'DI', 'L1', 'L2',
        'LP_reverse', 'MP_reverse', 'HP_reverse', 'LK_reverse', 'MK_reverse', 'HK_reverse', 'DI_reverse', 'L1_reverse', 'L2_reverse'
    ]
    
    xLP_LK = 0.5
    yLP_LK = 2.8
    # Define the circles' positions and sizes (x, y, radius)
    xLP = 28
    yLP = 15
    xMP = xLP + distance_between_centers * math.cos(angle_radians)
    yMP = yLP + distance_between_centers * math.sin(angle_radians)
    xHP = xMP + distance_between_centers
    yHP = yMP
    xLK = xLP - xLP_LK
    yLK = yLP - yLP_LK
    xMK = xMP - xLP_LK
    yMK = yMP - yLP_LK
    xHK = xHP - xLP_LK
    yHK = yHP - yLP_LK
    xDI_right, yDI_right, xDI, yDI = cal_equiliteral_triangle(xHP, yHP, xHK, yHK)
    xL2_right, yL2_right, xL2, yL2 = cal_equiliteral_triangle(xMK, yMK, xLK, yLK)
    xL1 = xLK - 1
    yL1 = yLK - 3.5

    circles = [
        (xLP, yLP, button_radius),  # LP
        (xMP, yMP, button_radius),  # MP
        (xHP, yHP, button_radius),  # HP
        (xLK, yLK, button_radius),  # LK
        (xMK, yMK, button_radius),  # MK
        (xHK, yHK, button_radius),  # HK
        (xDI_right, yDI_right, button_radius),  # DI
        (xL1, yL1, button_radius),  # L1
        (xL2_right, yL2_right, button_radius),  # L2
        # reverse
        (reverse_x(xLP, box_width), yLP, button_radius),  # LP_reverse
        (reverse_x(xMP, box_width), yMP, button_radius),  # MP_reverse
        (reverse_x(xHP, box_width), yHP, button_radius),  # HP_reverse
        (reverse_x(xLK, box_width), yLK, button_radius),  # LK_reverse
        (reverse_x(xMK, box_width), yMK, button_radius),  # MK_reverse
        (reverse_x(xHK, box_width), yHK, button_radius),  # HK_reverse
        (reverse_x(xDI_right, box_width), yDI_right, button_radius),  # DI_reverse
        (reverse_x(xL1, box_width), yL1, button_radius),  # L1_reverse
        (reverse_x(xL2_right, box_width), yL2_right, button_radius)  # L2_reverse
    ]
    # Prepare a dictionary to store points with names
    circle_points = {}

    for (x, y, radius), name in zip(circles, names):
        circle_points[name] = (x, y, radius)

    return circle_points.items()

def get_small_circle_points(box_width, box_height, pico_w):
    button_radius = 1.05
    xSelect = box_width / 2 - pico_w / 2 - 2.5
    ySelect = box_height - 1.5
    xStart = xSelect - 2.5
    yStart = ySelect
    names = ['Select', 'Start', 'Select_reverse', 'Start_reverse']
    
    circles = [
        (xSelect, ySelect, button_radius),
        (xStart, yStart, button_radius),
        (reverse_x(xSelect, box_width), ySelect, button_radius),
        (reverse_x(xStart, box_width), yStart, button_radius),
    ]
    
    circle_points = {}

    for (x, y, radius), name in zip(circles, names):
        circle_points[name] = (x, y, radius)

    return circle_points.items()
    

def draw_all_buttons(msp, box_width):
    for name, (x, y, radius) in get_big_circle_points():
        msp.add_circle((x, y), radius)
        
def draw_small_buttons(msp, box_width, box_height, pico_w):    
    for name, (x, y, radius) in get_small_circle_points(box_width, box_height, pico_w):
        msp.add_circle((x, y), radius)
        
def draw_all_screws(msp, box_width, box_height):
    button_radius = 0.2
    x10h = 1
    y10h = box_height - 1
    x2h = box_width - 1
    y2h = y10h
    x8h = x10h
    y8h = box_height - y2h
    x4h = x2h
    y4h = y8h
    x6h = box_width / 2
    y6h = y8h
    x11h = box_width / 2 - pico_w / 2 - 1
    y11h = y10h
    x1h = reverse_x(x11h, box_width)
    y1h = y11h

    circles = [
        (x10h, y10h, button_radius),
        (x2h, y2h, button_radius),
        (x8h, y8h, button_radius),
        (x4h, y4h, button_radius),
        (x6h, y6h, button_radius),
        (x11h, y11h, button_radius),
        (x1h, y1h, button_radius),
    ]
    
    for (x, y, radius) in circles:
        msp.add_circle((x, y), radius)
        
def draw_pico(msp, pico_w, pico_h):
    draw_usb(msp, 20, 20, pico_w, pico_h, pico_y_from_top)

def draw_pico_wire_connector(msp, pico_w, pico_h):
    rect_width = .3
    draw_usb(msp, 20 - pico_w / 2 + rect_width / 2, 20, rect_width, pico_h, pico_y_from_top)
    draw_usb(msp, 20 + pico_w / 2 - rect_width / 2, 20, rect_width, pico_h, pico_y_from_top)
    
def draw_ps5_pcb(msp):
    rect_height = 1.75
    draw_usb(msp, 35, 20, rect_height, rect_height, 0.6)
    
def draw_ps5_port(msp):
    rect_height = 1.45
    draw_usb(msp, 35, 20, rect_height, rect_height, 0)
    
def draw_switch_square(msp, center_point, side_length):
    x, y = center_point
    half_side = side_length / 2

    # Define the corners of the square
    points = [
        (x - half_side, y - half_side),
        (x + half_side, y - half_side),
        (x + half_side, y + half_side),
        (x - half_side, y + half_side),
        (x - half_side, y - half_side)  # Closing the square
    ]

    # Add the polyline to the model space
    msp.add_lwpolyline(points, close=True)
    
def draw_switch_footprint(msp, center_point):
    x, y = center_point
    draw_switch_square(msp, (x, y - .493), .3)
    hot_swap_radius = .15
    normal_radius = .12
    circles = [
        (x, y, .25), # center
        (x - .5, y - .515, .16), # stablized pin
        (x, y + .59, hot_swap_radius), # middle small pin
        (x + .5, y + .38, hot_swap_radius) # off angle small pin
    ]
    for x, y, radius in circles:
        msp.add_circle((x, y), radius)
        
def convert_dxf2img(file_name):
    # Create a new DXF document
    doc = ezdxf.readfile(file_name)
    msp = doc.modelspace()
    
    # Define dimensions in cm
    box_width_cm = 40
    box_height_cm = 20
    img_format = '.png'
    img_dpi = 300
    
    # Convert dimensions from cm to inches (1 inch = 2.54 cm)
    box_width_in = box_width_cm / 2.54
    box_height_in = box_height_cm / 2.54
    
    # Create a new figure with the specified size
    fig = plt.figure(figsize=(box_width_in, box_height_in))
    ax = fig.add_axes([0, 0, 1, 1])

    # Prepare the drawing context
    ctx = RenderContext(doc)
    ctx.set_current_layout(msp)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(msp, finalize=True)

    # Generate the output filename
    img_name = re.findall(r"(\S+)\.", file_name)  # Select the image name that is the same as the dxf file name
    first_param = ''.join(img_name) + img_format  # Concatenate list and string
    
    plt.subplots_adjust(left=2, right=10, top=10, bottom=0)

    # Save the figure with the specified DPI
    fig.savefig(first_param, transparent=True, dpi=img_dpi, pad_inches="layout", bbox_inches="tight")
    
    # Close the figure to free memory
    plt.close(fig)
    print(file_name, "Converted Successfully")
    
def add_padding(image_path, output_path, color=(255, 255, 255)):
    image = Image.open(image_path)
    
    # Calculate padding based on 10% of the original dimensions
    padding_width = int(image.width * 0.06)
    padding_height = int(image.height * 0.07)
    
    # Apply padding to the image
    padded_image = ImageOps.expand(image, border=(padding_width, padding_height), fill=(0, 0, 0))  # Fill color can be adjusted
    
    # Save the padded image
    padded_image.save(output_path)

        
def combine_hitbox_layout_and_image(image_name):
    layout_name = "layer-art.dxf"
    create_dxf_art(layout_name)
    convert_dxf2img(layout_name)
    add_padding(image_name, "added-padding.png", color=(255, 255, 255))
    background = Image.open("added-padding.png")
    hitbox_layer = Image.open(layout_name.replace(".dxf", ".png"))
    
    bg_rezised = background.resize(hitbox_layer.size)
    
    bg_rezised.paste(hitbox_layer, (0,0), hitbox_layer)
    bg_rezised.save("combined_layer.png")
    cropped_img = crop_black_margin("combined_layer.png")
    cropped_img.save("final.png")

def crop_black_margin(image_path):
    # Open the image
    img = Image.open(image_path)

    # Convert image to grayscale
    gray_img = img.convert("L")

    # Get the bounding box of the non-black areas
    bbox = gray_img.getbbox()

    # Crop the image using the bounding box
    if bbox:
        cropped_img = img.crop(bbox)
    else:
        cropped_img = img  # If the image is entirely black, return the original image

    return cropped_img

def create_dxf_layer1(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    msp = doc.modelspace()

    draw_all_buttons(msp, box_width)
    draw_small_buttons(msp, box_width, box_height, pico_w)
    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    
    # Save the DXF document
    doc.saveas(file_name)


def create_dxf_layer2(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    msp = doc.modelspace()

    draw_all_buttons(msp, box_width)
    draw_small_buttons(msp, box_width, box_height, pico_w)
    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    draw_usb_connector(msp)
    draw_pico(msp, pico_w, pico_h)
    draw_ps5_port(msp)
    
    draw_oled_wire(msp)
    draw_oled(msp, box_width, box_height, oled_width, oled_height)
    draw_oled_bottom(msp, .8)
    
    # Save the DXF document
    doc.saveas(file_name)   

    
def create_dxf_layer3(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    # doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    switch_width = 1.4
    for name, (x, y, radius) in get_big_circle_points():
        draw_switch_square(msp, (x, y), switch_width)
    for name, (x, y, radius) in get_small_circle_points(box_width, box_height, pico_w):
        draw_switch_square(msp, (x, y), switch_width)
        
    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    draw_usb_connector(msp)
    draw_pico(msp, pico_w, pico_h)
    draw_ps5_port(msp)
    
    draw_oled(msp, box_width, box_height, oled_width, oled_height)
    draw_oled_bottom(msp, 1)
    draw_oled_top(msp, .5)

    # Save the DXF document
    doc.saveas(file_name)
    
def create_dxf_layer4(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    # doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    for name, (x, y, radius) in get_big_circle_points() | get_small_circle_points(box_width, box_height, pico_w):
        draw_switch_footprint(msp, (x, y))

    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    draw_pico_wire_connector(msp, pico_w, pico_h)
    draw_ps5_port(msp)
    
    draw_oled_wire(msp)

    # Save the DXF document
    doc.saveas(file_name)
    
def create_dxf_layer5(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    # doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()
    pico_wire_w = 3
    pico_wire_h = 6

    draw_all_screws(msp, box_width, box_height)
    for name, (x, y, radius) in get_small_circle_points(box_width, box_height, pico_w):
        draw_switch_square(msp, (x, y), switch_width + .35)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    add_rounded_square(msp, box_width - 4, box_height - 4, corner_radius, (2, 2))
    draw_pico(msp, pico_wire_w, pico_wire_h)
    draw_ps5_pcb(msp)

    # Save the DXF document
    doc.saveas(file_name)

def create_dxf_layer6(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    # doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)

    # Save the DXF document
    doc.saveas(file_name)

def create_dxf_total(file_name):
    doc = ezdxf.new(dxfversion='R2010')
    create_dxf_layer1("layer1.dxf", doc) # 3mm
    create_dxf_layer2("layer2.dxf", doc) # 3mm
    create_dxf_layer3("layer3.dxf", doc) # 1.65mm
    create_dxf_layer4("layer4.dxf", doc) # 2mm
    create_dxf_layer5("layer5.dxf", doc) # 3mm
    create_dxf_layer6("layer6.dxf", doc) # 3mm
    doc.saveas(file_name)

        
def create_dxf_art(file_name, doc = ezdxf.new(dxfversion='R2010')):
    # Create a new DXF document
    # doc = ezdxf.new(dxfversion='R2010')
    msp = doc.modelspace()

    draw_all_buttons(msp, box_width)
    draw_small_buttons(msp, box_width, box_height, pico_w)
    draw_all_screws(msp, box_width, box_height)
    
    add_rounded_square(msp, box_width, box_height, corner_radius)
    draw_oled(msp, box_width, box_height, 3.4, 1.9)
    
    # Save the DXF document
    doc.saveas(file_name)


# Generate the DXF layout
create_dxf_total("total.dxf")
create_dxf_layer1("layer1.dxf") # 3mm
create_dxf_layer2("layer2.dxf") # 3mm
create_dxf_layer3("layer3.dxf") # 2mm
create_dxf_layer4("layer4.dxf") # 2mm
create_dxf_layer5("layer5.dxf") # 3mm
create_dxf_layer6("layer6.dxf") # 3mm

combine_hitbox_layout_and_image("stock.png") # stock ratio is 2 x 1
