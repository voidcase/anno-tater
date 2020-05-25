from os.path import isfile
from typing import Tuple, Callable, Union
from h5py import File
from PIL import Image

class H5Database:
    """
    Interfaces with an HDF5 file with the following structure:
    {frames}/
        {frame_name_000}/
            img (dataset)
            annotated_bbox
            pred/
                {model_name} (bbox)
        {frame_name_001}/ ...
        {frame_name_002}/ ...
        ...
    """

    SET_TRAIN = 0b0001
    SET_VALID = 0b0010
    SET_TEST  = 0b0100
    SET_SHIT  = 0b1000
    NAME_FRAMES_BASE = 'frames'
    NAME_ATTR_SUBSET = 'subset'
    NAME_DSET_IMAGE = 'img'
    NAME_ANNOTATION_BOUNDING_BOX = 'annotated_bounding_box'

    def __init__(self, filepath: str, base_path=None):
        if isfile(filepath):
            self.filepath = filepath
            self.base_path = base_path
        else:
            raise IOError(f'The specified file "{filepath}" does not exist')

    def _subset_selected(subset, selection):
        if selection & subset

    def list_frame_names(self, is_annotated: bool = None, subset: int):
        with File(self.filepath, 'r+') as fileroot:
            base = fileroot[self.base_path]
            children = list(base)
            if in_subset is not None:
                children = [
                    c for c in children
                    if base[c].attrs.get(self.NAME_ATTR_SUBSET) == in_subset
                ]
            if is_annotated is not None:
                children = [
                    c for c in children
                    if is_annotated == (self.NAME_ANNOTATION_BOUNDING_BOX in list(base[c]))
                ]
            return children

    def get_frame_image(self, frame_name: str) -> Image:
        with File(self.filepath, 'r') as fileroot:
            base = fileroot[self.base_path]
            arr = base[frame_name][self.NAME_DSET_IMAGE][:]
            return Image.fromarray(arr)

    def add_annotation(self, frame_name: str, bbox: Tuple[float, float, float, float]) -> None:
        """Add an annotation bounding box `bbox` to a frame with name `frame_name`."""
        with File(self.filepath, 'r+') as fileroot:
            frame = fileroot[self.base_path][frame_name]
            frame.create_dataset(self.NAME_ANNOTATION_BOUNDING_BOX, data=bbox)

    def get_annotation(self, frame_name: str, annotation_name) -> Tuple[float, float, float, float]:
        with File(self.filepath, 'r') as fileroot:
            return tuple(fileroot[self.base_path][frame_name][annotation_name][:])

    def set_frame_attr(self, frame_name: str, attr_key: str, value):
        with File(self.filepath, 'r+') as fileroot:
            fileroot[self.base_path][frame_name].attrs.create(attr_key, value)

    def assign_to_subset(self, frame_name: str, subset: int):
        assert isinstance(subset, int)
        self.set_frame_attr(frame_name, self.NAME_ATTR_SUBSET, subset)

