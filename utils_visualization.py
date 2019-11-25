import PIL
import pyperclip

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import os

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
    def __init__(self, filepath, filenames, n, columns, ind=0, figsize=None):
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

        self.fig = image_grid_plot(None, figsize=self.figsize, columns=self.columns)
        # move the upper left corner of figure at middle of screen's width
        plt.get_current_fig_manager().window.geometry("+" + str(int(screen_width/2)) + "+0")

        self.add_buttons()
        self.next_redraw(None)


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
        plt.draw()
        write_logs_ui("%d" % self.ind)
