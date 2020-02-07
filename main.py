import sys
import tkinter as tk
from pathlib import Path
from PIL import ImageTk, Image
import argparse

PROGNAME = 'anno-tater'

root = tk.Tk()
root.title(PROGNAME)

WIDTH = 1024
HEIGHT = 1024

def get_args():
    argp = argparse.ArgumentParser(
            prog=PROGNAME,
            description='Simple image annotator for single bounding boxes.',
            )
    argp.add_argument('image-directory', type=str)
    argp.add_argument('--filetype', type=str, default='')
    args = argp.parse_args()

csv_path = Path('./annotation.csv')
excluded_paths = []
with open(str(csv_path), 'r') as f:



# state
imdir = Path('/mxn/groups/pub/mlcrystals/hwr-dataset-collector/images_crystals')
pathgen = imdir.glob('**/*.jpg')
path = str(next(pathgen))
im = Image.open(path)
im = im.resize((WIDTH,HEIGHT), Image.ANTIALIAS)
img = ImageTk.PhotoImage(image=im)
x = 0
y = 0
bbox = [0,0,0,0]
mouse_down = False

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()
imframe = canvas.create_image(WIDTH//2, HEIGHT//2, image=img)

# canvas elements
vcrosshair = canvas.create_line(0, 0, 0, 0, fill='white')
hcrosshair = canvas.create_line(0, 0, 0, 0, fill='white')
rect = canvas.create_rectangle(bbox, outline='red')

def print_state():
    print(bbox, mouse_down)

def normalize_bbox(bbox):
    x1, y1, x2, y2 = bbox
    x = (x1 + x2) // 2
    y = (y1 + y2) // 2
    w = abs(x1 - x2)
    h = abs(y1 - y2)
    return x, y, w, h

def motion(event):
    global bbox, x, y
    x, y = event.x, event.y
    canvas.coords(hcrosshair,(0,y,WIDTH,y))
    canvas.coords(vcrosshair,(x,0,x,HEIGHT))
    if mouse_down:
        bbox[2], bbox[3] = (x, y)
    canvas.coords(rect, bbox)
    # print_state()

def start_rect(event):
    global bbox, x, y, mouse_down
    mouse_down = True
    bbox[0], bbox[1] = (x, y)

def finish_rect(event):
    global mouse_down
    mouse_down = False

def next_image(event):
    # write bbox
    global bbox, im, img, path
    print(f'{path}, {normalize_bbox(bbox)}')
    # load next image
    path = str(next(pathgen))
    im = Image.open(path)
    im = im.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(image=im)
    canvas.itemconfig(imframe, image=img)

# Bindings
canvas.bind('<Motion>', motion)
canvas.bind('<ButtonPress-1>', start_rect)
canvas.bind('<ButtonRelease-1>', finish_rect)
root.bind('<space>', next_image)
root.bind('q', lambda ev: sys.exit(0))

root.mainloop()
