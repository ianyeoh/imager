#!/bin/python3

import sys, os, argparse
import numpy as np
import math
from fractions import Fraction
from PIL import Image

# 10 levels of luminance represented in ASCII
ascii_scale = ' .:-=+*#%@'

# ANSI reset escape code
reset = '\033[0m'

'''
Returns the RGB escape code for the foreground colour in supported terminals.
'''
def rgbFG(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

'''
Returns the RGB escape code for the background colour in supported terminals.
'''
def rgbBG(r, g, b):
    return f'\033[48;2;{r};{g};{b}m'

def outputParameters(W, H, cols, rows, x_segment, y_segment, colour):    
    ratio1 = Fraction(W, H).limit_denominator()
    ratio2 = Fraction(cols, rows).limit_denominator()
    print(f'''      
        Generating image with parameters:
            Original resolution:        {rgbFG(48, 48, 48)}{W}x{H}{reset}
            Original aspect ratio:      {rgbFG(48, 48, 48)}{ratio1.numerator}:{ratio1.denominator}{reset}
            ASCII resolution:           {rgbFG(48, 48, 48)}{cols}x{rows}{reset}
            Final aspect ratio:         {rgbFG(48, 48, 48)}{ratio2.numerator}:{ratio2.denominator}{reset}
            Downscale ratio (no. 
            pixels to character):       {rgbFG(48, 48, 48)}{x_segment}x{y_segment}{reset}
            Colour:                     {rgbFG(48, 48, 48)}{colour}{reset}
            ''')

'''
Given an image object, scales the photo to the width of the terminal while maintaining aspect ratio
and returns the new resolution. If verbose is true, outputs information about the original and new image's 
resolution and aspect ratio.
'''
def getImageScale(image, verbose, colour):
    # Get terminal size
    t = os.get_terminal_size()
    
    # Get the pixel dimensions and calculate aspect ratio of the image
    W, H = image.size[0], image.size[1]
    # Final aspect ratio is halved to reduce the effect of line spacing
    ratio = (H/2)/W
    
    # Calculate the final resolution of image
    # The width of the final image is shrunk to fit the width of the terminal
    # Height is then scaled with aspect ratio
    x = t.columns
    y = int(ratio*x)
    
    # If the picture is smaller than the terminal size, display image in full resolution
    if W <= x:
        x_segment = 1
        y_segment = 1
        x = W
        y = H
    else:
        # Calculate number of pixels in each segment
        x_segment = W/x
        y_segment = H/y
    
    if verbose:
        outputParameters(W, H, x, y, x_segment, y_segment, colour)

    return (x, y)

'''
Given an image object, downscales the image to fit the terminal and returns the RGB colour values of each
pixel in a list, where each row is seperated in nested lists. Final RGB values are stored as a 3-tuple.
'''
def convertImageToColour(img, verbose):
    img = img.convert('RGB')
    
    scale = getImageScale(img, verbose, True)
    cols = scale[0]
    rows = scale[1]

    img = img.resize((cols, rows))

    # RGB colour data formatted as a list for each row in the image, 
    # and each item in the row is a pixel with 3-tuple of the pixel's RGB values
    colours = []
    c = np.array(img)
    
    for row in range(rows):
        colours.append([])
        
        for col in range(cols):
            colours[row].append((
                c[row][col][0],
                c[row][col][1],
                c[row][col][2]
                ))
    
    return colours

'''
Given an image object, downscales the image to fit the terminal and converts each pixel's luminance value
to the corresponding ASCII character. Returns a list of strings, with each string representing a row.
'''
def convertImageToASCII(img, verbose):
    img = img.convert('L')
    
    scale = getImageScale(img, verbose, True)
    cols = scale[0]
    rows = scale[1]

    img = img.resize((cols, rows))

    asciimg = []
    c = np.array(img)
    
    for row in range(rows):
        asciimg.append('')
        
        for col in range(cols):
            ascii_chr = ascii_scale[int((c[row][col]*9)/255)]
            asciimg[row] += ascii_chr
    
    return asciimg

def main():
    # Parse args
    parser = argparse.ArgumentParser(
        prog = 'imager',
        description = 'Generates an ASCII image from an image file'
    )
    parser.add_argument('filename')
    parser.add_argument('-v', action='store_true', dest='verbose', required=False)
    parser.add_argument('-c', action='store_true', dest='colour', required=False)
    
    args = parser.parse_args()

    # Open image file
    try:
        img = Image.open(args.filename)
    except FileNotFoundError:
        print(f'imager: error: File not found: {args.filename}')
        sys.exit()

    if args.colour:
        image = convertImageToColour(img, args.verbose)
        for row in image:
            for pixel in row:
                sys.stdout.write(f'{rgbBG(pixel[0], pixel[1], pixel[2])} {reset}')
            print()
    else:
        image = convertImageToASCII(img, args.verbose)
        for row in image:
            print(f'{row}')
    
    img.close()

if __name__ == "__main__":
    main()