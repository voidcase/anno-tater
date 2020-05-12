import sys
import tkinter as tk
from pathlib import Path
from PIL import ImageTk, Image
import argparse
from typing import Tuple
import csv


def get_args():
    argp = argparse.ArgumentParser(
            prog=AnnoTater.PROGNAME,
            description='Simple image annotator for single bounding boxes.',
            )
    argp.add_argument('dir', type=str, help='directory to read images from')
    argp.add_argument('-o', '--output',
                      help='csv file to write to',
                      default='./annotations.csv')
    argp.add_argument('-t', '--filetype', type=str, default='jpg')
    argp.add_argument('--height', type=int, help='height of window in pixels', default=1024)
    argp.add_argument('--width', type=int, help='width of window in pixels', default=1024)
    argp.add_argument('--modify', action='store_true')
    return argp.parse_args()


def normalize_bbox(bbox: Tuple[int, int, int, int]):
    x1, y1, x2, y2 = bbox
    x = (x1 + x2) // 2
    y = (y1 + y2) // 2
    w = abs(x1 - x2)
    h = abs(y1 - y2)
    return x, y, w, h


class AnnoTater:

    PROGNAME = 'anno-tater'

    def __init__(self, size: Tuple[int, int], imdir: Path, filetype:str, outfile: Path, modmode: bool):
        self.root = root = tk.Tk()

        self.modmode = modmode
        self.width = size[0]
        self.height = size[1]
        self.imdir = imdir
        self.outfile = outfile
        self.paths = list(imdir.glob(f'**/*.{filetype}'))
        self.pathindex = 0
        print(len(self.paths))
        if outfile.exists():
            with open(outfile, 'r') as f:
                csvreader = csv.reader(f)
                donepaths = [row[0] for row in csvreader]
                if self.modmode:
                    self.paths = donepaths
                else:
                    self.paths = [p for p in self.paths if str(p) not in donepaths]
        print(len(self.paths))

        # Initialize state
        self.bbox = [0,0,0,0]
        self.mouse_down = False
        self.tkim = self.load_image(0)
        
        # Create UI elements
        self.root.title(self.PROGNAME)
        self.canvas = canvas = tk.Canvas(root, width=self.width, height=self.height)
        canvas.pack()
        self.imframe = self.canvas.create_image(
                self.width//2,
                self.height//2,
                image=self.tkim
                )
        self.vcrosshair = canvas.create_line(0, 0, 0, 0, fill='blue')
        self.hcrosshair = canvas.create_line(0, 0, 0, 0, fill='blue')
        self.rect = canvas.create_rectangle(self.bbox, outline='red')
        self.text = canvas.create_text(
                10,10,
                text=self.get_corner_text(),
                anchor='nw',
                fill='blue',
                )
        self.cursor_text = canvas.create_text(
                0,0,
                text='',
                anchor='sw',
                fill='blue',
                )

    def get_corner_text(self):
        return '[{}/{}] - {}'.format(
                self.pathindex,
                len(self.paths),
                self.paths[self.pathindex].stem
                )

    def write_bbox(self, path, bbox):
        with open(self.outfile, 'a') as f:
            csvwriter = csv.writer(f)
            csvwriter.writerow([path, *bbox])

    def motion(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.hcrosshair, (0, y, self.width, y))
        self.canvas.coords(self.vcrosshair, (x, 0, x, self.height))
        if self.mouse_down:
            self.bbox[2:] = (x, y)
        self.canvas.coords(self.rect, self.bbox)
        self.canvas.coords(self.cursor_text, (x, y))
        self.canvas.itemconfig(self.cursor_text, text=f' x:{x} y:{y}')

    def start_rect(self, event):
        self.mouse_down = True
        self.bbox[0], self.bbox[1] = (event.x, event.y)

    def finish_rect(self, event):
        self.mouse_down = False

    def load_image(self, idx):
        im = Image.open(self.paths[idx])
        im = im.resize((self.width, self.height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image=im)

    def next_image(self, event):
        self.write_bbox(self.paths[self.pathindex], self.bbox)
        if self.pathindex == len(self.paths):
            print('reached end of pathlist, exiting')
            sys.exit(0)
        self.pathindex += 1
        self.tkim = self.load_image(self.pathindex)
        self.canvas.itemconfig(self.imframe, image=self.tkim)
        self.canvas.itemconfig(self.text, text=self.get_corner_text())

    def create_bindings(self):
        root = self.root
        canvas = self.canvas
        canvas.bind('<Motion>', self.motion)
        canvas.bind('<ButtonPress-1>', self.start_rect)
        canvas.bind('<ButtonRelease-1>', self.finish_rect)
        root.bind('<space>', self.next_image)
        root.bind('q', lambda ev: sys.exit(0))

    def run(self):
        self.create_bindings()
        self.root.mainloop()


if __name__ == '__main__':
    args = get_args()
    print(args)
    assert Path(args.dir).exists()
    app = AnnoTater(
            size=(args.height, args.width),
            imdir=Path(args.dir),
            filetype=args.filetype,
            outfile=Path(args.output),
            modmode=args.modify,
            )
    app.run()
