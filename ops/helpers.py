import math

class Pitch():
    def __init__(self, max_texture_size, item_count):
        self.y_count = math.ceil(item_count / max_texture_size)
        if self.y_count > 1:
            self.max = max_texture_size
            self.width = max_texture_size
            self.x = 1 / max_texture_size
            self.y = 1 / self.y_count
        else:
            self.max = max_texture_size
            self.width = item_count
            self.x = 1 / item_count
            self.y = 1

    def max_frame_count(self):
        return math.floor(self.max / self.y_count)

    def pos_from_index(self, index):
        pos = [0.0] * 2
        pos[0] = (index % self.max) * self.x + (self.x * 0.5)
        pos[1] = math.floor(index / self.max) * self.y
        return pos

    def pixel_from_index(self, index, frame_count, cur_frame):
        pos = [0] * 2
        pos[0] = index % self.max
        pos[1] = math.floor(index / self.max) * frame_count + cur_frame
        return pos

    def frame_offset(self, frame_count):
        return self.y / frame_count

    def index_from_pos(self, pos):
        epsilon = 0.001
        x_index = (pos[0] - (self.x * 0.5)) / self.x
        y_index = pos[1] / self.y
        index = (self.width * math.floor(y_index)) + math.floor(x_index)
        return index if (x_index - math.floor(x_index) < epsilon) and (y_index - math.floor(y_index) < epsilon) else None
