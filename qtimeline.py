
from PyQt4 import QtCore, QtGui

__author__ = 'cgdougm'


##########################################
class FrameTimeline(QtGui.QGraphicsScene):

    def __init__(self, parent=None):
        super(FrameTimeline, self).__init__(parent)
        self.height = 30
        #
        self.startTime = 1
        self.endTime = 100
        self.timeSpace = 10
        self.currentTime = None
        #
        self.unitsPerTime = 5
        #
        self.setBackgroundBrush(QtCore.Qt.lightGray)
        #
        # l = QtGui.QGraphicsAnchorLayout()
        # l.setSpacing(0)
        # self.setLayout(l)
        #
        self._frame_bar_rect_item = None
        self._frame_bar_text_items = list()

    @property
    def time_range(self):
        return self.endTime - self.startTime

    def build(self):
        self.build_frame_bar()
        if self.currentTime is not None:
            self.build_current_time()
        self.update_positions()

    def build_frame_bar(self):
        self._frame_bar_text_items = list()
        r = self.addRect(0,
                         0,
                         self.time_range,
                         self.height,
                         QtGui.QPen(QtCore.Qt.transparent),
                         QtGui.QBrush(QtCore.Qt.darkGray))
        drop = QtGui.QGraphicsDropShadowEffect()
        drop.setBlurRadius(6.0)
        drop.setOffset(4.0, 4.0)
        r.setGraphicsEffect(drop)
        self._frame_bar_rect_item = r
        for t in range(self.startTime, self.endTime, self.timeSpace):
            textItem = self.addText(str(t))
            textItem.setPos(t * self.unitsPerTime, 0.0)
            self._frame_bar_text_items.append(textItem)

    def build_current_time(self):
        tx = self.currentTime * self.unitsPerTime
        current_background = self.addRect(-2, -2, 30, 30, QtGui.QBrush(QtCore.Qt.black))
        current_background.setOpacity(0.2)
        current_background.setPos(tx, 0.0)
        current_text_item = self.addText(str(self.currentTime))
        current_text_item.setPos(tx, 0.0)
        bold_font = current_text_item.font()
        bold_font.setBold(True)
        current_text_item.setFont(bold_font)

    def update_positions(self):
        # Rectangle
        transform = self._frame_bar_rect_item.transform()
        transform.reset()
        transform.scale(self.unitsPerTime, 1.0)
        self._frame_bar_rect_item.setTransform(transform)
        # Text
        for i, t in enumerate(range(self.startTime, self.endTime, self.timeSpace)):
            text = self._frame_bar_text_items[i]
            text.setPos(t * self.unitsPerTime, 0.0)


##########################################
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    g = FrameTimeline()
    g.build()

    class DemoView(QtGui.QGraphicsView):

        def __init__(self, parent=None):
            super(DemoView, self).__init__(parent)
            self.setSceneRect(0, 0, 600, 400)

        def wheelEvent(self, event):
            delta = float(event.delta()) / 120.0
            g.unitsPerTime += delta
            g.update_positions()

    w = DemoView()
    w.setScene(g)

    w.show()

    sys.exit(app.exec_())

