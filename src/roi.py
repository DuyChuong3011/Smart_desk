class ROIManager:
    def __init__(self, config):
        self.roi = config['desk']['roi']
        self.x1, self.y1 = self.roi['x1'], self.roi['y1']
        self.x2, self.y2 = self.roi['x2'], self.roi['y2']

    def is_inside_roi(self, point):
        x, y = point
        return (self.x1 <= x <= self.x2) and (self.y1 <= y <= self.y2)

    def filter_detections(self, detections):
        return [d for d in detections if self.is_inside_roi(d['center'])]
