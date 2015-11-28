
__author__ = 'cgdougm'

from PyQt4 import QtCore, QtGui


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
        #l = QtGui.QGraphicsAnchorLayout()
        #l.setSpacing(0)
        #self.setLayout(l)
        #
        self._framebarRectItem = None
        self._framebarTextItems = list()


    @property
    def timeRange(self):
        return self.endTime - self.startTime

    def build(self):
        self.buildFrameBar()
        if self.currentTime is not None:
            self.buildCurrentTime()
        self.updatePositions()

    def buildFrameBar(self):
        self._framebarTextItems = list()
        r = self.addRect(0, 0, self.timeRange, self.height,
                     QtGui.QPen(QtCore.Qt.transparent),
                     QtGui.QBrush(QtCore.Qt.darkGray))
        drop = QtGui.QGraphicsDropShadowEffect()
        drop.setBlurRadius(6.0)
        drop.setOffset(4.0, 4.0)
        r.setGraphicsEffect(drop)
        self._framebarRectItem = r
        for t in range(self.startTime, self.endTime, self.timeSpace):
            textItem = self.addText(str(t))
            textItem.setPos(t * self.unitsPerTime, 0.0)
            self._framebarTextItems.append(textItem)

    def buildCurrentTime(self):
        tx = self.currentTime * self.unitsPerTime
        currBg = self.addRect(-2, -2, 30, 30, brush=QtGui.QBrush(QtCore.Qt.black))
        currBg.setOpacity(0.2)
        currBg.setPos(tx, 0.0)
        currTextItem = self.addText(str(self.currentTime))
        currTextItem.setPos(tx, 0.0)
        boldFont = currTextItem.font()
        boldFont.setBold(True)
        currTextItem.setFont(boldFont)

    def updatePositions(self):
        # Rectangle
        transf = self._framebarRectItem.transform()
        transf.reset()
        transf.scale(self.unitsPerTime, 1.0)
        self._framebarRectItem.setTransform(transf)
        # Text
        for i, t in enumerate(range(self.startTime, self.endTime, self.timeSpace)):
            text = self._framebarTextItems[i]
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
            g.updatePositions()

    w = DemoView()
    w.setScene(g)

    w.show()

    sys.exit(app.exec_())

