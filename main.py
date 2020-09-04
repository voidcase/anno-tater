#!/usr/bin/env python3

import sys
import argparse
from typing import Tuple, List
import tkinter as tk
from PIL import ImageTk, Image
from mxaimbot_common.h5db import H5Database
from mxaimbot_common import util


def get_args():
    parser = argparse.ArgumentParser(
        prog=AnnoTater.PROGNAME,
        description='Simple image annotator for single bounding boxes.',
    )
    parser.add_argument(
        'db',
        type=str,
        help='hdf5 file containing dataset to annotate. Will both read and write.'
    )
    parser.add_argument(
        '--height',
        type=int,
        help='height of window in pixels',
        default=1024
    )
    parser.add_argument(
        '--width',
        type=int,
        help='width of window in pixels',
        default=1024
    )
    parser.add_argument('--inspect', action='store_true')
    return parser.parse_args()


class AnnoTater:
    """
    GUI for annotating images with bounding boxes.
    """
    #pylint: disable=too-many-instance-attributes

    PROGNAME = 'anno-tater'

    def __init__(self, window_size: Tuple[int, int], db: H5Database, inspect_mode=False):
        self.root = root = tk.Tk()
        self.width = window_size[0]
        self.height = window_size[1]
        self.db = db
        self.inspect_mode = inspect_mode
        if self.inspect_mode:
            self.paths = db.list_frame_names(
                is_annotated=True,
                include_bad=False,
                sort_by_time=True,
                in_subset=db.SET_TEST,
            )

        else:
            self.paths = db.list_frame_names(
                is_annotated=False,
                include_bad=False,
                sort_by_time=True
            )

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
        self.rect_center = canvas.create_text(0, 0, text='.', fill='red', anchor='s')
        self.rect_text = canvas.create_text(50, 50, text='AAAAA', fill='red', anchor='nw')
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
        self.predictions: List[Tuple[int, int]] = [] # rectangle_id text_id

    def get_corner_text(self) -> str:
        "Returns text to display in the corner of the screen."
        return '[{}/{}] - {}'.format(
            self.pathindex,
            len(self.paths),
            self.paths[self.pathindex],
        )

    def write_bbox(self, path, bbox):
        normalized_bbox = util.xyxy_to_scaled_xywh(bbox, (self.height, self.width))
        self.db.add_annotation(path, normalized_bbox)

    def next_image(self, step=1):
        if self.pathindex == len(self.paths):
            print('reached end of pathlist, exiting')
            sys.exit(0)
        self.pathindex += step
        self.tkim = self.load_image(self.pathindex)
        self.canvas.itemconfig(self.imframe, image=self.tkim)
        self.canvas.itemconfig(self.text, text=self.get_corner_text())
        if self.inspect_mode:
            # undisplay previous predictions
            for rect, text in self.predictions:
                self.canvas.delete(rect)
                self.canvas.delete(text)
            self.predictions = []
            # display predictions
            for name, bbox in self.db.get_predictions(self.paths[self.pathindex]):
                print(name, bbox)
                xyxy = util.scaled_xywh_to_xyxy(bbox, (self.height, self.width))
                rect = self.canvas.create_rectangle(xyxy, outline='blue')
                text = self.canvas.create_text(xyxy[:2], text=name, fill='blue', anchor='nw')
                self.predictions.append((rect, text))


            existing_anno = self.db.get_annotation(self.paths[self.pathindex])
            existing_anno_xyxy = util.scaled_xywh_to_xyxy(existing_anno, (self.height, self.width))
            self.canvas.coords(self.rect, existing_anno_xyxy)
            self.canvas.coords(self.rect_text, existing_anno_xyxy[:2])
            self.canvas.itemconfig(self.rect_text, text="annotation")

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
        self.canvas.coords(self.rect_center, util.xyxy_to_xywh(self.bbox)[:2])
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
        if not self.inspect_mode:
            canvas.bind('<Motion>', self.on_motion)
            canvas.bind('<ButtonPress-1>', self.start_rect)
            canvas.bind('<ButtonRelease-1>', self.finish_rect)
            root.bind('d', self.mark_bad)
            root.bind('<space>', self.confirm_and_proceed)
        root.bind('q', lambda ev: sys.exit(0))
        root.bind('s', self.skip)
        root.bind('<Left>', self.undo)
        root.bind('z', self.undo)
        root.bind('<Right>', self.skip)

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
        inspect_mode=args.inspect
    )
    app.run()
