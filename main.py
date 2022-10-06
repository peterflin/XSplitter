from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import ui
import os
import numpy as np
import math
from picarray import *
from PIL import Image
import time
import random
# import result_view as view_dialog


class Main(QMainWindow, ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.color = {
            0: "#FFFFFF",
            1: "#000000"
        }
        self.setupUi(self)
        # cut2 = cv2.resize(cut, (16, 16), interpolation=cv2.INTER_AREA)
        height, width, channel = cut.shape
        bytesPerline = 4 * width
        cut_qimg = QImage(cut.data, width, height, bytesPerline, QImage.Format.Format_RGBA8888)
        self.setWindowIcon(QIcon(QPixmap.fromImage(cut_qimg)))
        # self.setWindowIcon(QIcon('cut.png'))
        # img = cv2.imread("teach.png")
        img = np.array(teach)
        # img = cv2.resize(img, (274, 226), interpolation=cv2.INTER_AREA)
        height, width, channel = img.shape
        bytesPerline = 3 * width
        qImg = QImage(img.data, width, height, bytesPerline, QImage.Format.Format_RGB888)
        self.label_7.setPixmap(QPixmap.fromImage(qImg))
        self.lineEdit_4.setText(os.path.abspath("./"))
        self.pushButton.clicked.connect(self.load_image)
        self.pushButton_2.clicked.connect(self.split)
        self.pushButton_3.clicked.connect(self.set_output_dir)
        # self.preview_btn.clicked.connect(self.preview)
        # self.label.setScaledContents(True)
        self.lineEdit.setReadOnly(True)
        self.lineEdit_4.setReadOnly(True)
        self.comboBox.currentIndexChanged.connect(self.change_color_view)
        self.color_view.setStyleSheet(f"background-color: {self.color[self.comboBox.currentIndex()]};border: 2px solid black;")
        self.add_new_color_btn.clicked.connect(self.add_new_color)

    def load_image(self):
        qfd = QFileDialog(self)
        file = qfd.getOpenFileName(None, "開啟檔案", os.path.abspath("./"), "圖像檔 (*.png, *.jpg, *.jpeg, *.*)")
        if file[0] == '':
            return
        self.lineEdit.setText(file[0])
        # self.label.setPixmap(QPixmap("IU_153.jpg"))
        # self.label.show()  # You were missing this.
        # img = cv2.imread("D:/work/雜/image_cutter/IU_153.jpg")

        img = Image.open(file[0])
        img.load()
        img = np.asarray(img, dtype="uint8")[:, :, 0:3]
        if img.size == 1:
            return
        filled_img = self.fill_img(img, 300, 600)
        height, width, channel = filled_img.shape
        bytesPerline = 4 * width
        # qImg = QImage(img.data, width, height, bytesPerline, QImage.Format.Format_RGB888)  # .rgbSwapped()
        qImg = QImage(filled_img.data, width, height, bytesPerline, QImage.Format.Format_RGBA8888)  # .rgbSwapped()
        # if img_shape_type == 0:
        #     self.label.setGeometry(350 - int(w/2), 270, w, h)
        # else:
        #     self.label.setGeometry(100, 270, w, h)
        # print(self.label.geometry())
        self.label.setPixmap(QPixmap.fromImage(qImg))

    def fill_img(self, img, label_h, label_w):
        w, h = img.shape[1], img.shape[0]
        img_shape_type = 0
        h_ratio = label_h / h if h > label_h else 1
        w_ratio = label_w / w if w > label_w else 1
        ratio = min(h_ratio, w_ratio)
        h *= ratio
        w *= ratio
        if w > h:
            img_shape_type = 1
        h = int(h)
        h = h - h % 2
        w = int(w)
        w = w - w % 2
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
        height, width, channel = img.shape
        filled_img = np.ones((label_h, label_w, 4), dtype=np.int8)
        filled_img[:, :, 0:3] *= 255
        half_h = label_h // 2
        half_w = label_w // 2
        filled_img[half_h - height // 2: half_h + height // 2, half_w - width // 2: half_w + width // 2, :3] = img
        filled_img[half_h - height // 2: half_h + height // 2, half_w - width // 2: half_w + width // 2, 3] *= 255
        return filled_img

    def split(self):
        img_path = self.lineEdit.text()
        output_path = self.lineEdit_4.text()
        line = self.lineEdit_2.text()
        row = self.lineEdit_3.text()
        if img_path == "" or output_path == "" or row == "" or line == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("錯誤！")
            msg.setInformativeText("設置尚未完成！")
            msg.setWindowTitle("錯誤訊息")
            msg.setDetailedText("設置尚未完成，請確認設定資訊是否正確。")
            msg.exec_()
            return
        self.image_splitting(img_path, output_path, int(row), int(line), self.color[self.comboBox.currentIndex()])

    def set_output_dir(self):
        qfd = QFileDialog(self)
        directory = qfd.getExistingDirectory(None, "瀏覽路徑", os.path.abspath("./"))
        if directory == '':
            return
        self.lineEdit_4.setText(directory)

    def image_splitting(self, imagePath, outputPath, rows=2, columns=3, background='w'):

        # assert background == 'w' or background == 'b', 'background should be "b"(black) or "w"(white).'
        assert isinstance(rows, int) and isinstance(columns,
                                                    int), 'rows and columns should be integer and greater than 1.'

        img = Image.open(imagePath)
        img.load()
        img = np.asarray(img, dtype="uint8")[:, :, 0:3]
        tileSize = math.ceil(max(img.shape[0] / rows, img.shape[1] / columns))

        newFolder = os.path.join(outputPath, os.path.splitext(os.path.basename(imagePath))[0])
        try:
            if not os.path.isdir(newFolder):
                os.makedirs(newFolder)
            else:
                for f in os.listdir(newFolder):
                    os.remove(os.path.join(newFolder, f))
                os.rmdir(newFolder)
                os.makedirs(newFolder)
        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("程式錯誤！")
            msg.setInformativeText("請確認是否有同檔名的資料夾")
            msg.setWindowTitle("錯誤")
            msg.setDetailedText("程式錯誤，請確認是否有同檔名的資料夾，若有的話請手動刪除該資料夾。")
            msg.exec()
            return

        bg_color = [int(background[1:3], base=16), int(background[3:5], base=16), int(background[5:7], base=16)]
        BG = np.zeros(shape=(tileSize * rows, tileSize * columns, 3)).astype('uint8')
        BG[:, :] = bg_color

        offset_y = int((BG.shape[0] - img.shape[0]) / 2)
        offset_x = int((BG.shape[1] - img.shape[1]) / 2)
        BG[offset_y:offset_y + img.shape[0], offset_x:offset_x + img.shape[1], :] = img
        k = 1
        for i in range(rows):
            for j in range(columns):
                temp = BG[tileSize * i:tileSize * (i + 1), tileSize * j:tileSize * (j + 1), :]
                temp = Image.fromarray(temp)
                temp.save(os.path.join(newFolder, "%d.jpg" % (k)))
                k += 1
        num = 10
        progress = QProgressDialog(self)
        progress.setWindowTitle("執行中")
        progress.setLabelText("正在操作...")
        progress.setCancelButtonText("取消")
        progress.setMinimumDuration(5)
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, num)
        for i in range(num):
            progress.setValue(i)
            time.sleep(random.random())
            if progress.wasCanceled():
                QMessageBox.warning(self, "提示", "操作失败")
                break
        else:
            progress.setValue(num)
            QMessageBox.information(self, "提示", "操作成功")
        print(f"successfully generate {k - 1} image tiles")
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        # msg.setText("成功！")
        # msg.setInformativeText("完成切割")
        # msg.setWindowTitle("完成")
        # msg.setDetailedText("完成切割，請至輸出路徑確認。")
        # msg.exec_()
        return

    def change_color_view(self):
        self.color_view.setStyleSheet(f"background-color: {self.color[self.comboBox.currentIndex()]};border: 2px solid black;")

    def add_new_color(self):
        color = QColorDialog.getColor()
        # self.color_view.setStyleSheet(
        #     f"background-color: {color.name()};border: 2px solid black;")
        if color.name() in self.color.values():
            return
        self.comboBox.addItem(color.name().upper())
        self.color[len(self.color)] = color.name()
        self.comboBox.setCurrentIndex(self.comboBox.count() - 1)

    def preview(self):
        image_path = self.lineEdit.text()
        print(image_path)
        # outputPath = self.lineEdit_4.text()
        # newFolder = os.path.join(outputPath, os.path.splitext(os.path.basename(image_path))[0])
        # pic_list = []
        # for f_name in sorted(os.listdir(newFolder)):
        #     img = Image.open(f_name)
        #     img.load()
        #     img = np.asarray(img, dtype="uint8")[:, :, 0:3]
        #     pic_list.append(img)
        dialog = QtWidgets.QDialog()
        preview = PreviewController(dialog, image_path)
        dialog.exec()


# class PreviewController(QDialog, view_dialog.Ui_Dialog):
#     def __init__(self, dialog, image_path, rows=2, columns=3, background='#FFFFFF'):
#         super().__init__()
#         self.setupUi(dialog)
#         # self.image_view.setText(image_path)
#         cut_result = self.image_splitting(image_path, rows, columns, background)
#         self.show_image(cut_result, dialog, rows, columns)
#
#     def show_image(self, images, dialog, len_row, len_col):
#         start_x = 10
#         start_y = 10
#         labels = [[QtWidgets.QLabel(dialog) for j in range(len_col)] for i in range(len_row)]
#         for r_idx in range(len_row):
#             for c_idx in range(len_col):
#                 # lb = QtWidgets.QLabel(dialog)
#                 lb = labels[r_idx][c_idx]
#                 lb.setGeometry(QRect(10, 10, 400, 400))
#                 lb.setText("")
#                 lb.setObjectName(f"label_{r_idx}_{c_idx}")
#                 img_idx = r_idx * len_row + c_idx
#         #         # print(images[img_idx].image)
#         #         # height, width, channel = images[img_idx].shape
#         #         # bytesPerline = 4 * width
#         #
#                 # q_img = QImage(images[img_idx], width, height, bytesPerline, QImage.Format.Format_RGBA8888)
#                 q_img = images[img_idx].toqimage()
#                 print(q_img.format())
#                 # lb.setPixmap(QPixmap.fromImage())
#                 break
#
#     def fill_img(self, img, label_h, label_w):
#         w, h = img.shape[1], img.shape[0]
#         img_shape_type = 0
#         h_ratio = label_h / h if h > label_h else 1
#         w_ratio = label_w / w if w > label_w else 1
#         ratio = min(h_ratio, w_ratio)
#         h *= ratio
#         w *= ratio
#         if w > h:
#             img_shape_type = 1
#         h = int(h)
#         h = h - h % 2
#         w = int(w)
#         w = w - w % 2
#         img = cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)
#         height, width, channel = img.shape
#         filled_img = np.ones((label_h, label_w, 4), dtype=np.int8)
#         filled_img[:, :, 0:3] *= 255
#         half_h = label_h // 2
#         half_w = label_w // 2
#         filled_img[half_h - height // 2: half_h + height // 2, half_w - width // 2: half_w + width // 2, :3] = img
#         filled_img[half_h - height // 2: half_h + height // 2, half_w - width // 2: half_w + width // 2, 3] *= 255
#         return filled_img
#
#     def image_splitting(self, image_path, rows=2, columns=3, background='w'):
#
#         # assert background == 'w' or background == 'b', 'background should be "b"(black) or "w"(white).'
#         assert isinstance(rows, int) and isinstance(columns,
#                                                     int), 'rows and columns should be integer and greater than 1.'
#
#         img = Image.open(image_path)
#         img.load()
#         img = np.asarray(img, dtype="uint8")[:, :, 0:3]
#         tileSize = math.ceil(max(img.shape[0] / rows, img.shape[1] / columns))
#
#         bg_color = [int(background[1:3], base=16), int(background[3:5], base=16), int(background[5:7], base=16)]
#         BG = np.zeros(shape=(tileSize * rows, tileSize * columns, 3)).astype('uint8')
#         BG[:, :] = bg_color
#
#         offset_y = int((BG.shape[0] - img.shape[0]) / 2)
#         offset_x = int((BG.shape[1] - img.shape[1]) / 2)
#         BG[offset_y:offset_y + img.shape[0], offset_x:offset_x + img.shape[1], :] = img
#         k = 1
#         result_set = []
#         for i in range(rows):
#             for j in range(columns):
#                 temp = BG[tileSize * i:tileSize * (i + 1), tileSize * j:tileSize * (j + 1), :]
#                 temp = Image.fromarray(temp)
#                 result_set.append(temp)
#                 k += 1
#         return result_set


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
