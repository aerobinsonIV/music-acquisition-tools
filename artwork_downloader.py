from tkinter import *
from tkinter import ttk
from typing import List
from PIL import Image, ImageTk
import math

THUMBNAIL_SIZE = 200
ZOOM_BOX_HEIGHT = 600

class CoverArtSelector():
    def motion(self, event):
        # Buttons have 5px padding, subtract to get exact coords relative to image
        x, y = event.x - 5, event.y - 5
        widget = event.widget

        try:
            self.image_index = int(widget._name)
        except:
            # We're not on an image
            self.image_index = -1
            pass

        if self.image_index != -1:

            # Even if the mouse is on a button, it may still be outside the image. 
            # If it's in the small padding area on the edge, we don't consider it to be on an image.
            if x < 0 or y < 0:
                self.image_index = -1

            if x > THUMBNAIL_SIZE or y > THUMBNAIL_SIZE:
                self.image_index = -1

        if self.image_index != -1:
            # TODO: Is there a way to do this mapping using pillow?
            original_image = self.images_pil_resized[self.image_index]
            original_image_size = original_image.width
            coord_multiplier = original_image_size / THUMBNAIL_SIZE

            mapped_x = x * coord_multiplier
            mapped_y = y * coord_multiplier

            # TODO: use this as an excuse to learn those weird question mark oneliners because the goal is to become a snobby code elitist
            if mapped_x > self.zoom_box_width / 2:
                # Calc x based on right edge
                right = mapped_x + math.ceil(self.zoom_box_width / 2)
                if right > original_image_size:
                    right = original_image_size
                left = right - self.zoom_box_width
            else:
                # Calc x based on left edge
                left = mapped_x - math.floor(self.zoom_box_width / 2)
                if left < 0:
                    left = 0
                right = left + self.zoom_box_width

            if mapped_y > self.zoom_box_width / 2:
                # Calc y based on bottom edge
                bottom = mapped_y + math.ceil(ZOOM_BOX_HEIGHT / 2)
                if bottom > original_image_size:
                    bottom = original_image_size
                top = bottom - ZOOM_BOX_HEIGHT
            else:
                # Calc y based on top edge
                top = mapped_y - math.floor(ZOOM_BOX_HEIGHT / 2)
                if top < 0:
                    top = 0
                bottom = top + ZOOM_BOX_HEIGHT

            box_tuple = (left, top, right, bottom)
            zoom_box_image = original_image.crop(box_tuple)
            
            zoom_box_image_tk = ImageTk.PhotoImage(zoom_box_image)
            self.zoom_box_label.configure(image=zoom_box_image_tk)

            self.anti_garbage_collection_list[0] = zoom_box_image_tk

    def __init__(self, images: List) -> None:
        # Load all thumnbail images
        # TODO: Ensure these are all square, do centered cropping if they aren't
        self.images_pil = []
        for image in images:
            self.images_pil.append(image)

    def show_selection_window(self) -> int:  
        num_thumbnails = len(self.images_pil)

        self.root = Tk()

        self.zoom_box_width = num_thumbnails * THUMBNAIL_SIZE + (num_thumbnails - 1) * 10 # Calculate zoom area width
        image_pil = Image.new(mode="RGB", size =(self.zoom_box_width, ZOOM_BOX_HEIGHT)) # Create placeholder image for zoom area
        zoom_box_image_tk = ImageTk.PhotoImage(image_pil) # Make placeholder image into ImageTK

        # Hack to prevent the zoomed image from getting garbage collected by TCL
        # See https://stackoverflow.com/a/71502573
        self.anti_garbage_collection_list = []
        self.anti_garbage_collection_list.append(zoom_box_image_tk)

        ttk.Label(self.root, name="zoom_box", image=zoom_box_image_tk).grid(column=0, row=0, columnspan=num_thumbnails + 1)
        self.zoom_box_label = self.root.children["zoom_box"]

        # Create thumbnail buttons
        self.images_tk = []
        for i in range(len(self.images_pil)):
            image_pil = self.images_pil[i].resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE))
            self.images_tk.append(ImageTk.PhotoImage(image_pil))
            ttk.Button(self.root, name=str(i), image=self.images_tk[-1], command=self.root.destroy).grid(column=i, row=1)

        # If any of the original images are smaller than the width of the zoomed area, scale them up
        self.images_pil_resized = []
        for i in range(num_thumbnails): 
            width = self.images_pil[i].width
            if width < self.zoom_box_width:
                size_multiplier = math.floor(self.zoom_box_width / width) + 1
            else:
                # Double zoom of even high-res images just so we can get a better look at the details
                size_multiplier = 2
            
            self.images_pil_resized.append(self.images_pil[i].resize((width * size_multiplier, width * size_multiplier), resample=Image.Resampling.NEAREST))

        self.root.bind('<Motion>', self.motion)
        self.root.mainloop()
        return self.image_index

# List is a list of pillow images
def choose_image(images: List):
    selector = CoverArtSelector(images)
    return selector.show_selection_window()

if __name__ == "__main__":
    artwork_images = []
    for i in range(1, 6):
        artwork_images.append(Image.open(f"D:\\soundscrape\\temp_artwork\\{i}.jpg"))

    print(choose_image(artwork_images))
    