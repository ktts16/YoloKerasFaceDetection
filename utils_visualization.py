import PIL
import pyperclip

import tkinter as tk
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os

import cv2
import numpy as np
from DFInterface import *

def get_display_resolution():
    root = tk.Tk()
    width_pixel = root.winfo_screenwidth()
    height_pixel = root.winfo_screenheight()

    width_inch = root.winfo_screenmmwidth() * 1/25.4 #MM_TO_IN
    dpi = width_pixel/width_inch
    root.destroy() #close window
    return width_pixel, height_pixel, dpi


def write_logs_ui(line):
    file_logs_ui = os.path.join(os.getcwd(),"logs_ui.txt")
    # If file exists, append ("a"). Otherwise, create file ("w").
    mode = "a" if os.path.exists(file_logs_ui) else "w"
    with open(file_logs_ui, mode) as text_file:
        if mode == "w":
            text_file.write("# last FileNameIterator.ind" + "\n")
        text_file.write(line + "\n")


def get_indices_of_next_n_items(l, start_index, n):
    if start_index < 0 or start_index > len(l):
        raise Exception("'start_index' must be within range [0, {}] because list l is of length {}".format(len(l)-1, len(l)))
    return (start_index, start_index+n)


def get_indices_of_prev_n_items(l, end_index, n):
    if end_index > len(l)-1 or end_index < n-1:
        raise Exception("'end_index' must be within range [{}, {}] because list l is of length {}".format(n-1, len(l)-1, len(l)))
    start = end_index-n+1
    return (start, end_index+1)


def loop_each_n_items(l, n, start_index=0, end_index=0):
    end_i = end_index
    if end_index == 0:
        if start_index == 0:
            end_i = len(l)-n+1
        else:
            end_i = start_index+n
    for i in range(start_index,end_i,n):
        yield l[i:i+n]


# Source: https://nbviewer.jupyter.org/gist/minrk/7076095

def open_images(image_path, list_filenames):
    return [PIL.Image.open(os.path.join(image_path, f)) for f in list_filenames]


def onclick(event):
    if event.inaxes is not None:
        # the axes object on which the user clicked
        ax = event.inaxes
        # can use ax.children() to find which img artist is in this axes and extract the data from it

        subplot_label = ax.get_label()

        # copy subplot's label to clipboard
        pyperclip.copy(subplot_label.split(".")[0])


def create_annotations_in_figure_2(fig, dfif):
    for axes in fig.get_axes():
        if is_type_AxesSubplot(axes):
            search_str = axes.get_title()
            row = dfif.get_df_row(search_str)
            if len(row.index) == 1:
                index = row.index.tolist()[0]
                axes.set_title('')
                axes.set_label('%d' % index)
            text = dfif.df_row_to_str(row)
            annot = make_annotation(axes, text, (10, 10))
            annot.set_visible(True)


def image_grid_plot(images, figsize=(20,20), columns=5, fig=None):
    if fig is None:
        fig = plt.figure(figsize=figsize)
    if images is not None:
        # remove all axes (subplots) except the first two (buttons)
        for ax in fig.get_axes()[2:]:
            ax.remove()
        for i, image in enumerate(images):
            filepath_parts = image.filename.split('/')
            sub = plt.subplot(len(images) / columns + 1, columns, i + 1, label=filepath_parts[-1])
            sub.clear()
            sub.set_title(filepath_parts[-2] + '/' + filepath_parts[-1], fontsize=12)
            plt.imshow(image)
            sub.axes.set_axis_off() #hide subplot's axes

    # when mouse button pressed, call onclick function
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    # make subplots has no margin
    fig.subplots_adjust(bottom=0.05, top=0.95, left=0, right=1, wspace=0.0)
    return fig


class FileNameIterator(object):
    def __init__(self, filepath, filenames, n, columns, df=None, ind=0, figsize=None):
        self.filenames = filenames
        self.filepath = filepath
        self.n = n
        self.ind = ind
        screen_width, screen_height, dpi = get_display_resolution()
        if figsize is not None:
            self.figsize = figsize
        else:
            # make figure size: half of screen's width and screen's height
            self.figsize = (screen_width/2/dpi, screen_height/dpi)
        self.columns = columns
        self.df = df # data frame
        self.dfif = IMDBInterface(df)

        self.fig = image_grid_plot(None, figsize=self.figsize, columns=self.columns)
        # move the upper left corner of figure at middle of screen's width
        plt.get_current_fig_manager().window.geometry("+" + str(int(screen_width/2)) + "+0")

        self.add_buttons()
        self.next_redraw(None)
        self.create_annotations()


    def add_buttons(self):
        # source: https://matplotlib.org/3.1.0/gallery/widgets/buttons.html
        # add Next and Previous butttons
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        self.bnext = Button(axnext, 'Next')
        self.bnext.on_clicked(self.next_redraw)

        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        self.bprev = Button(axprev, 'Previous')
        self.bprev.on_clicked(self.prev_redraw)


    def update_ind(self, new_ind):
        if new_ind >= self.n-1 and new_ind < len(self.filenames):
            self.ind = new_ind


    def next(self):
        ##get next set of image file names
        inds = get_indices_of_next_n_items(self.filenames, self.ind, self.n)
        self.update_ind(inds[-1]-1)
        return self.filenames[inds[0]:inds[1]]


    def prev(self):
        ##get previous set of image file names
        inds = get_indices_of_prev_n_items(self.filenames, self.ind, self.n)
        self.update_ind(inds[0])
        return self.filenames[inds[0]:inds[1]]


    def next_redraw(self, event):
        self.redraw(self.next())


    def prev_redraw(self, event):
        self.redraw(self.prev())


    def redraw(self, files):
        self.fig = image_grid_plot(open_images(self.filepath, files), figsize=self.figsize, columns=self.columns, fig=self.fig)
        self.create_annotations()
        plt.draw()
        write_logs_ui("%d" % self.ind)

    def create_annotations(self):
        if self.dfif is not None:
            create_annotations_in_figure_2(self.fig, self.dfif)


def image_with_box_and_points(img, pts, highlight_color = (255,155,0), box = None):
    image = img.copy()
    if box is not None:
        cv2.rectangle(image,
                      (box[0], box[1]),
                      (box[0]+box[2], box[1] + box[3]),
                      highlight_color,
                      2)
    for p in pts:
        cv2.circle(image,(p[0], p[1]), 2, highlight_color, 2)
    return image


def image_with_landmarks(img, result):
    # Result is an array with all the bounding boxes detected. We know that for 'ivan.jpg' there is only one.
    bounding_box = result[0]['box']
    keypoints = result[0]['keypoints']

    pts = np.array([keypoints['left_eye'], keypoints['right_eye'], 
        keypoints['nose'], keypoints['mouth_left'], keypoints['mouth_right']])
    return image_with_box_and_points(img, pts, highlight_color=(255,155,0), box = bounding_box)


def image_with_points(img, pts, highlight_color = (0,0,255)):
    return image_with_box_and_points(img, pts, highlight_color = highlight_color)


# > Annotations
def make_annotation(ax, text, pos, pos_text=(0,0)):
    return ax.annotate(text, xy=pos, xytext=pos_text, textcoords="offset points",
                       bbox=dict(boxstyle="round", fc="w"))


def get_annotations(ax, filter_type=mpl.text.Annotation):
    annotations = [child for child in ax.get_children() if isinstance(child, filter_type)]
    has_one_element = len(annotations) == 1
    if has_one_element:
        return (annotations[0], has_one_element)
    else:
        return (annotations, has_one_element)


def is_type_AxesSubplot(obj):
    return issubclass(type(obj), mpl.axes.SubplotBase)
