import matplotlib
import os
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from scipy import misc
from matplotlib.lines import Line2D
from matplotlib import interactive
interactive(True)
from annotate import Annotator
from shapely.geometry import Polygon
from shapely.geometry import Point


# TODO: note that y is from bottom
class BoxBuilder:
    def __init__(self):
        self.jump_step = 20
        self.fig = plt.figure(1)
        self.ann = Annotator()
        self.xs = []
        self.ys = []
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('click to build box segments')
        self.show = None
        # box is  x1, x2, x3, x4
        self.all_box_in_one_image = []
        self.all_boxes_to_write = self.ann.boxes.copy()
        self.image = []
        self.stop = False

        # register event for mouse click and keyboard press
        self.cid_m_click = self.fig.canvas.mpl_connect('button_press_event', self.mouse_click)
        self.cid_k_press = self.fig.canvas.mpl_connect('key_press_event', self.on_key)

        self.reload_image()

    # draw boxes detected by machine
    def init_draw(self):
        for xs, ys in self.all_box_in_one_image:
            xs.append(xs[0])
            ys.append(ys[0])
            self.ax.add_line(Line2D(xs, ys, color='r'))

    def left_click(self, event):
        """
        if detect left click, may
        :param event:
        :return:
        """
        if not (event.xdata and event.ydata):
            return
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)

        # TODO: now is quadrilateral, may need segmentation, just add a button for stop sign instead of 4
        if len(self.xs) == 4:
            # self.fig.canvas.mpl_disconnect(self.cid)
            self.all_box_in_one_image.append((self.xs[0:4], self.ys[0:4]))
            self.xs.append(self.xs[0])
            self.ys.append(self.ys[0])
            self.stop = True

        self.ax.add_line(Line2D(self.xs, self.ys, color='#ee2020'))

        if self.stop:
            self.xs = []
            self.ys = []
            self.stop = False

    def right_click(self, event):
        x = event.xdata
        y = event.ydata
        nearest_ind = self.find_nearest(x, y)
        if nearest_ind != -1:
            del self.all_box_in_one_image[nearest_ind]
            self.reload_image(clear=False)

    # if mouse clicked, call this function
    def mouse_click(self, event):
        """
        deal with mouse input
        :param event:
        :return:
        """

        if event.button == 1:
            self.left_click(event)
        elif event.button == 3:
            self.right_click(event)

    def on_key(self, event):
        """
        deal with the keyboard input
        :param event:
        :return:
        """
        if event.key == 'n':
            if self.ann.index < len(self.ann.img_names) - 1:
                self.ann.index += 1
                self.reload_image()
            else:
                self.finish()

        elif event.key == 'b':
            if self.ann.index > 0:
                self.ann.index -= 1
                self.reload_image()
            else:
                print("ouch, my head")
        elif event.key == 'j':
            if self.ann.index < len(self.ann.img_names) - self.jump_step:
                self.ann.index += self.jump_step
                self.reload_image()
            else:
                print("no jump anymore")

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_m_click)

    def get_polygon(self):
        """
        change all box in this image to polygon
        :return:  a list of polygon
        """
        polygons = []
        for box in self.all_box_in_one_image:
            poly_format = []
            for i in range(4):
                poly_format.append((box[0][i], box[1][i]))
            polygon = Polygon(poly_format)
            polygons.append(polygon)
        return polygons

    def find_nearest(self, x, y):
        """
        helper function for finding the nearest box if right click
        :return:
        """
        polygons = self.get_polygon()
        point = Point(x, y)
        min_dist = 100000
        min_index = 0
        # find the nearest polygon centroid
        for index, polygon in enumerate(polygons):
            distance = point.distance(polygon.centroid)
            if distance < min_dist:
                min_dist = distance
                min_index = index
        if min_dist > 60:
            min_index = -1
        return min_index

    def finish(self):
        print("wow finished")
        name = self.ann.img_name
        self.all_boxes_to_write[name] = self.all_box_in_one_image
        self.ann.save_csv(self.all_boxes_to_write)
        plt.close(self.fig)

    def clear(self):
        """
        clear data before start labeling new image
        :return: 
        """
        self.xs = []
        self.ys = []
        self.all_box_in_one_image = []

    def reload_image(self, clear=True):
        """
        load image, not necessary "next"
        it depends on the current index
        :return: 
        """
        if clear:
            name = self.ann.img_name
            self.all_boxes_to_write[name] = self.all_box_in_one_image
            self.clear()

            name = self.ann.next()
            # name = name.split('.')[0]
            if name in self.ann.boxes:
                bboxes = self.ann.boxes[name].copy()
                self.all_box_in_one_image = bboxes
            else:
                self.all_box_in_one_image = []

        self.ax.clear()
        plt.imshow(self.ann.image)
        if self.all_box_in_one_image:
            self.init_draw()

if __name__ == '__main__':
    box_builder = BoxBuilder()
    plt.show(block=True)

