
from PyQt4 import QtCore, QtGui

__author__ = 'cgdougm'


##########################################
class TimelineTag(object):
    """
    Tags a frame number with a text label
    """

    def __init__(self, name=None, frame=None):
        self.name = name
        self.frame = frame

    @property
    def label(self):
        return self.name or str(self.frame) or "?"


##########################################
class QTimelineTag(QtGui.QGraphicsItemGroup, TimelineTag):
    """
    A polygon and text representing a TimelineTag
    """

    def __init__(self, name=None, frame=None, scene=None):
        TimelineTag.__init__(self, name, frame)
        QtGui.QGraphicsItemGroup.__init__(self)
        self.rectangle_pen = QtGui.QPen(QtCore.Qt.transparent)
        self.rectangle_color = QtGui.QColor(0, 0, 0, int(0.25 * 255))
        self.rectangle_brush = QtGui.QBrush(self.rectangle_color)
        self.label_pen = QtGui.QPen(QtCore.Qt.transparent)
        self.label_brush = QtGui.QBrush(QtCore.Qt.white)
        self.rectangle = None
        self.label_text = None
        self.line_item = None
        self.line_item_pen = QtGui.QPen(self.rectangle_color)
        self.line_item_pen.setStyle(QtCore.Qt.DashLine)
        self.build()
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemSendsScenePositionChanges, True)

    def build(self):
        polygon_width = 10 * len(self.label) # cbb
        polygon_height = 20
        polygon_arrow_height = 6
        ul = QtCore.QPointF(-polygon_width * 0.5, 0.0)
        ur = QtCore.QPointF(+polygon_width * 0.5, 0.0)
        lr = QtCore.QPointF(+polygon_width * 0.5, polygon_height)
        ll = QtCore.QPointF(-polygon_width * 0.5, polygon_height)
        arrow = QtCore.QPointF(0.0, polygon_height + polygon_arrow_height)
        line_point = QtCore.QPointF(arrow)
        line_point.setY(500)
        self.rectangle = QtGui.QGraphicsPolygonItem(QtGui.QPolygonF([ul, ur, lr, arrow, ll]))
        self.rectangle.setPen(self.rectangle_pen)
        self.rectangle.setBrush(self.rectangle_brush)
        self.label_text = QtGui.QGraphicsSimpleTextItem(self.label)
        self.label_text.setPos(-len(self.label) * 10.0 / 4, 0.0)  # hack for now
        self.label_text.setPen(self.label_pen)
        self.label_text.setBrush(self.label_brush)
        self.line_item = QtGui.QGraphicsLineItem(QtCore.QLineF(arrow, line_point))
        self.line_item.setPen(self.line_item_pen)
        for item in (self.rectangle, self.label_text, self.line_item):
            self.addToGroup(item)

    def paint(self, *args):
        self.rectangle.paint(*args)
        self.label_text.paint(*args)
        self.line_item.paint(*args)

    def itemChange(self, change, variant):
        value = variant.toPyObject()
        print change, value, QtGui.QGraphicsItem.ItemPositionChange
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            value.setY(40.0)
        return QtGui.QGraphicsItemGroup.itemChange(self, change, value)


##########################################
class FrameTimeline(QtGui.QGraphicsScene):
    """
    This scene contains a
        frame bar (the start to end frame numbers with the current frame)
        tag bar (string-named frame numbers)
        actions bar (the visual or audio actions that have start and end frames)
            actions are grouped
            actions have cues
                cue connects to start, end or middle of actions with offsets
                cues can connect to tags.

    """

    def __init__(self, parent=None):
        super(FrameTimeline, self).__init__(parent)
        self.frame_bar_height = 30
        self.tag_bar_height = 40
        #
        self.start_frame = 1
        self.end_frame = 100
        self.frame_number_stride = 10
        self.current_frame = None
        #
        self.initial_screen_units_per_frame = 5
        self.screen_units_per_frame = 5
        #
        self.setBackgroundBrush(QtCore.Qt.lightGray)
        self.transparent_pen = QtGui.QPen(QtCore.Qt.transparent)
        #
        self._frame_bar_rect_item = None
        self._frame_bar_text_items = list()
        #
        self.tags = list()
        self._tag_bar_rect_item = None
        self._tag_bar_line_items = list()
        self._tag_bar_polygon_items = list()
        self._tag_bar_text_items = list()

    def add_tag(self, name, frame):
        self.tags.append(TimelineTag(name, frame))

    @property
    def time_range(self):
        return self.end_frame - self.start_frame

    def build(self):
        self.build_frame_bar()
        if self.current_frame is not None:
            self.build_current_time()
        self.build_tag_bar()
        self.update_positions()

    def build_frame_bar(self):
        # Bar rectangle
        self._frame_bar_text_items = list()
        self._frame_bar_rect_item = self.addRect(0,
                                                 0,
                                                 self.time_range,
                                                 self.frame_bar_height,
                                                 self.transparent_pen,
                                                 QtGui.QBrush(QtCore.Qt.darkGray))
        drop_shadow_effect = QtGui.QGraphicsDropShadowEffect()
        drop_shadow_effect.setBlurRadius(6.0)
        drop_shadow_effect.setOffset(4.0, 4.0)
        self._frame_bar_rect_item.setGraphicsEffect(drop_shadow_effect)
        # Numbers
        for frame_number in range(self.start_frame, self.end_frame, self.frame_number_stride):
            self._frame_bar_text_items.append(self.addText(str(frame_number)))

    def build_current_time(self):
        # Rectangle
        current_background = self.addRect(-2, -2, 30, 30, QtGui.QBrush(QtCore.Qt.black))
        current_background.setOpacity(0.2)
        current_background.setPos(self.current_frame * self.screen_units_per_frame, 0.0)
        # Text
        current_text_item = self.addText(str(self.current_frame))
        current_text_item.setPos(self.current_frame * self.screen_units_per_frame, 0.0)
        bold_font = current_text_item.font()
        bold_font.setBold(True)
        current_text_item.setFont(bold_font)

    def build_tag_bar(self):
        # Reset list of graphics items
        self._tag_bar_line_items = list()
        self._tag_bar_polygon_items = list()
        self._tag_bar_text_items = list()
        # Rectangle
        self._tag_bar_rect_item = self.addRect(0,
                                               self.frame_bar_height + 2,
                                               self.time_range,
                                               self.tag_bar_height,
                                               QtGui.QPen(QtCore.Qt.transparent),
                                               QtGui.QBrush(QtCore.Qt.darkGray))
        drop_shadow_effect = QtGui.QGraphicsDropShadowEffect()
        drop_shadow_effect.setBlurRadius(6.0)
        drop_shadow_effect.setOffset(4.0, 4.0)
        self._tag_bar_rect_item.setGraphicsEffect(drop_shadow_effect)
        # Tags
        for tag in self.tags:
            tag_item = QTimelineTag(tag.name, tag.frame, self)
            self.addItem(tag_item)
            self._tag_bar_text_items.append(tag_item)

    def frame_under_mouse(self, x, y):
        local_point = self._frame_bar_rect_item.mapFromScene(x, y)
        frame = int(local_point.x())
        return frame

    def update_positions(self, center_on=None):
        # Transform that allows horizontal scaling of the timeline (screen_units_per_frame factor)
        timeline_scale_transform = QtGui.QTransform().scale(float(self.screen_units_per_frame), 1.0)
        if center_on is None:
            center_on = self.start_frame
        x_offset = -(center_on - self.start_frame) * (self.screen_units_per_frame - self.initial_screen_units_per_frame)
        x_offset /= self.screen_units_per_frame
        timeline_scale_transform.translate(x_offset, 1.0)

        #
        #  Frame bar 
        #
        
        #  Rectangle
        self._frame_bar_rect_item.setTransform(timeline_scale_transform)

        # Text
        for i, t in enumerate(range(self.start_frame, self.end_frame, self.frame_number_stride)):
            text = self._frame_bar_text_items[i]
            text.setPos(t * self.screen_units_per_frame + x_offset, 0)
        
        #
        #  Tag bar
        #
        
        # Rectangle
        self._tag_bar_rect_item.setTransform(timeline_scale_transform)

        # Polygon, Text
        for tag, tag_item in zip(self.tags, self._tag_bar_text_items):
            tag_item.setPos(tag.frame * self.screen_units_per_frame + x_offset, self.frame_bar_height + 8)


##########################################
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    g = FrameTimeline()
    g.add_tag("testing", 23)
    g.build()

    class DemoView(QtGui.QGraphicsView):

        def __init__(self, parent=None):
            super(DemoView, self).__init__(parent)
            self.setSceneRect(0, 0, 600, 400)

        def wheelEvent(self, event):
            delta = float(event.delta()) / 120.0
            g.screen_units_per_frame += delta
            g.screen_units_per_frame = max(1, g.screen_units_per_frame)
            frm = g.frame_under_mouse(event.x(), event.y())
            g.update_positions(center_on=frm)

            # l = QtGui.QGraphicsAnchorLayout()
            # l.setSpacing(0)
            # self.setLayout(l)

    w = DemoView()
    w.setScene(g)

    w.show()

    sys.exit(app.exec_())
