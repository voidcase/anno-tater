import sys
import tkinter as tk
from pathlib import Path
from PIL import ImageTk, Image
import argparse
from typing import Tuple

def get_args():
    argp = argparse.ArgumentParser(
            prog=PROGNAME,
            description='Simple image annotator for single bounding boxes.',
            )
    argp.add_argument('image-directory', type=str)
    argp.add_argument('--filetype', type=str, default='')
    args = argp.parse_args()

class AnnoTater:

    PROGNAME = 'anno-tater'

    def __init__(self, size: Tuple[int, int], imdir: Path, outfile: Path):
        self.width = width = size[0]
        self.height = height = size[1]
        self.imdir = imdir
        self.outfile = outfile

        self.x = 0
        self.y = 0
        self.bbox = [0,0,0,0]
        self.mouse_down = False
        self.path = None
        self.im = None
        self.tkim = None

        self.root = root = tk.Tk()
        self.root.title(self.PROGNAME)
        self.canvas = canvas = tk.Canvas(root, width=width, height=height)
        canvas.pack()
        self.imframe = self.canvas.create_image(WIDTH//2, HEIGHT//2, image=tkim)

        # canvas elements
        self.vcrosshair = canvas.create_line(0, 0, 0, 0, fill='blue')
        self.hcrosshair = canvas.create_line(0, 0, 0, 0, fill='blue')
        self.rect = canvas.create_rectangle(bbox, outline='red')

    def normalize_bbox(bbox):
        x1, y1, x2, y2 = bbox
        x = (x1 + x2) // 2
        y = (y1 + y2) // 2
        w = abs(x1 - x2)
        h = abs(y1 - y2)
        return x, y, w, h

    def motion(self, event):
        bbox, x, y = self.bbox, self.x, self.y
        self.x, self.y = event.x, event.y
        canvas.coords(hcrosshair,(0,y,WIDTH,y))
        canvas.coords(vcrosshair,(x,0,x,HEIGHT))
        if mouse_down:
            bbox[2], bbox[3] = (x, y)
        canvas.coords(rect, bbox)
        # print_state()

    def start_rect(event):
        self.mouse_down = True
        self.bbox[0], self.bbox[1] = (self.x, self.y)

    def finish_rect(event):
        self.mouse_down = False

    def next_image(event):
        global bbox, im, img, path
        print(f'{path}, {normalize_bbox(bbox)}')
        # load next image
        path = str(next(pathgen))
        im = Image.open(path)
        im = im.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image=im)
        canvas.itemconfig(imframe, image=img)

    def create_mappings():
        canvas.bind('<Motion>', motion)
        canvas.bind('<ButtonPress-1>', start_rect)
        canvas.bind('<ButtonRelease-1>', finish_rect)
        root.bind('<space>', next_image)
        root.bind('q', lambda ev: sys.exit(0))

    def run(self):
        pass


if __name__ == '__main__':
    app = AnnoTater()
    app.run()

#####################################################################################


excluded_paths = []



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


def print_state():
    print(bbox, mouse_down)


# Bindings

root.mainloop()
