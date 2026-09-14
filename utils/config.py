import numpy as np
from collections import defaultdict, deque

class TrackHistoryManager:
    """Stores spatial positions across time to analyze trajectory and speed."""
    def __init__(self, max_history=30):
        self.history = defaultdict(lambda: deque(maxlen=max_history))

    def update(self, detections):
        active_ids = set()
        for det in detections:
            t_id = det["track_id"]
            if t_id != -1:
                self.history[t_id].append(det["center"])
                active_ids.add(t_id)
        return active_ids

    def get_trajectory(self, track_id):
        return list(self.history[track_id])

    def calculate_velocity(self, track_id, fps=30.0):
        pts = self.history[track_id]
        if len(pts) < 5:
            return 0.0
        
        p1 = np.array(pts[-5])
        p2 = np.array(pts[-1])
        dist_px = np.linalg.norm(p2 - p1)
        time_sec = 4.0 / fps
        return float(dist_px / time_sec) if time_sec > 0 else 0.0
