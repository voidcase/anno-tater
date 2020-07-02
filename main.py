#!/usr/bin/env python3

import sys
import tkinter as tk
from pathlib import Path
from PIL import ImageTk, Image
import argparse
from typing import Tuple, Set
from h5db import H5Database


def get_args():
    argp = argparse.ArgumentParser(
        prog=AnnoTater.PROGNAME,
        description='Simple image annotator for single bounding boxes.',
    )
    argp.add_argument('db', type=str,
                      help='hdf5 file containing dataset to annotate. Will both read and write.')
    argp.add_argument('--height', type=int, help='height of window in pixels', default=1024)
    argp.add_argument('--width', type=int, help='width of window in pixels', default=1024)
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

    def __init__(self, window_size: Tuple[int, int], db: H5Database):
        self.root = root = tk.Tk()
        self.width = window_size[0]
        self.height = window_size[1]
        self.db = db
        self.paths = db.list_frame_names(is_annotated=False, include_bad=False, sort_by_time=True)
        self.pathindex = 0

        # Initialize state
        self.bbox = [0, 0, 0, 0]
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
        self.rectmid = canvas.create_text(0, 0, text='.', fill='red')
        self.text = canvas.create_text(
            10, 10,
            text=self.get_corner_text(),
            anchor='nw',
            fill='blue',
        )
        self.cursor_text = canvas.create_text(
            0, 0,
            text='',
            anchor='sw',
            fill='blue',
        )

    def get_corner_text(self):
        return '[{}/{}] - {}'.format(
            self.pathindex,
            len(self.paths),
            self.paths[self.pathindex],
        )

    def write_bbox(self, path, bbox):
        self.db.add_annotation(path, bbox)

    def next_image(self, step=1):
        if self.pathindex == len(self.paths):
            print('reached end of pathlist, exiting')
            sys.exit(0)
        self.pathindex += step
        self.tkim = self.load_image(self.pathindex)
        self.canvas.itemconfig(self.imframe, image=self.tkim)
        self.canvas.itemconfig(self.text, text=self.get_corner_text())

    def load_image(self, idx):
        im = Image.fromarray(self.db.get_frame_image(self.paths[idx]))
        im = im.resize((self.width, self.height), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image=im)

    #### EVENT HANDLERS ####
    
    def on_motion(self, event):
        x, y = event.x, event.y
        self.canvas.coords(self.hcrosshair, (0, y, self.width, y))
        self.canvas.coords(self.vcrosshair, (x, 0, x, self.height))
        if self.mouse_down:
            self.bbox[2:] = (x, y)
        self.canvas.coords(self.rect, self.bbox)
        self.canvas.coords(self.rectmid, normalize_bbox(self.bbox)[:2])
        self.canvas.coords(self.cursor_text, (x, y))
        self.canvas.itemconfig(self.cursor_text, text=f' x:{x} y:{y}')

    def start_rect(self, event):
        self.mouse_down = True
        self.bbox[0], self.bbox[1] = (event.x, event.y)

    def finish_rect(self, event):
        self.mouse_down = False

    def confirm_and_proceed(self, event):
        self.write_bbox(self.paths[self.pathindex], self.bbox)
        self.next_image()

    def mark_bad(self, event):
        self.db.assign_to_subset(self.paths[self.pathindex], self.db.SET_SHIT)
        self.next_image()

    def skip(self, event):
        self.next_image()

    def undo(self, event):
        self.next_image(step=-1)


    def create_bindings(self):
        root = self.root
        canvas = self.canvas
        canvas.bind('<Motion>', self.on_motion)
        canvas.bind('<ButtonPress-1>', self.start_rect)
        canvas.bind('<ButtonRelease-1>', self.finish_rect)
        root.bind('<space>', self.confirm_and_proceed)
        root.bind('q', lambda ev: sys.exit(0))
        root.bind('s', self.skip)
        root.bind('d', self.mark_bad)
        root.bind('z', self.undo)

    def run(self):
        self.create_bindings()
        self.root.mainloop()


if __name__ == '__main__':
    args = get_args()
    print(args)
    db = H5Database(args.db, base_path='frames')
    app = AnnoTater(
        window_size=(args.height, args.width),
        db=db,
    )
    app.run()
