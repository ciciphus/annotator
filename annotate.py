from scipy import misc

import os
import csv


class Annotator:
    def __init__(self):
        # image processing now
        self.image = []
        # the bounding box of all images, dict
        self.boxes = {}
        # bounding box that are processing now, [([x1, x2, x3, x4], [y1, y2, y3, y4]), (x1, ...)]
        self.box = []
        # represent mode is add or remove 0 is delete , 1 is add
        self.mode = 0
        self.index = 0

        # read from path
        self.r_csv_path = '/Users/ci.chen/temp/no-use/73018_new_result.csv'
        self.w_csv_path = '/Users/ci.chen/temp/no-use/73018_new_result.csv'

        self.read_csv()

        self.img_dir = '/Users/ci.chen/vic_img/'
        # self.img_dir = '/Users/ci.chen/temp/no-use/test/'
        self.img_name = '00046622.jpg'
        self.img_path = os.path.join(self.img_dir, self.img_name)
        self.img_names = []
        self.get_img_names()
        self.read_img(self.img_path)

    def next(self):
        """
        get next image
        """
        self.img_name = self.img_names[self.index]
        self.img_path = os.path.join(self.img_dir, self.img_name)
        self.read_img(self.img_path)
        return self.img_name

    def read_img(self, img_path):
        """
        :param
        img_path: path to the image
        read image
        :return: Image
        """
        self.image = misc.imread(img_path)

    def read_csv(self):
        """
        read prelabeled labels into dictionary
        :return:
        """
        with open(self.r_csv_path, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')

            last_pic = ''

            positions = []
            for i, row in enumerate(reader):
                xs = []
                ys = []
                if not i:
                    continue
                datum = row[0].split(',')

                if "\"" in datum[0]:
                    name = datum[0].split('\"')[3]
                    if len(name.split('.')) == 1:
                        name = name + '.jpg'
                else:
                    name = datum[0]

                # print(name)

                for index, coord in enumerate(datum):
                    if index % 2 == 1:
                        xs.append(int(coord))
                    elif index and index % 2 == 0:
                        ys.append(int(coord))

                if last_pic != name and last_pic:
                    self.boxes[last_pic] = positions
                    positions = []

                positions.append((xs, ys))
                last_pic = name

        self.boxes[last_pic] = positions


    def save_csv(self, boxes):
        """
        save new labels as csv
        :return:
        """
        rows = [["image", "x1", "y1", "x2", "y2", 'x3', 'y3', 'x4', 'y4']]
        # print(boxes)
        for name, box in boxes.items():
            for single_box in box:
                # name = name.split('.')[0]
                row = [name]
                # print(single_box)

                for i in range(4):
                    row.append(int(single_box[0][i]))
                    row.append(int(single_box[1][i]))
                rows.append(row)

        def writeCSV(rows):
            with open(self.w_csv_path, 'w') as File:
                writer = csv.writer(File)
                writer.writerows(rows)

        writeCSV(rows)

    def get_img_names(self):
        """
        helper function to get image names in the folder
        :return:
        """
        file_names = os.listdir(self.img_dir)
        for file_name in file_names:
            if file_name.endswith(".jpg") or file_name.endswith(".png"):
                self.img_names.append(file_name)



