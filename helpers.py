import math
import bpy
import bmesh

class ChannelParams(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    min: bpy.props.IntProperty(name="Min")
    max: bpy.props.IntProperty(name="Max")


class Tex(bpy.types.PropertyGroup):
    red: bpy.props.CollectionProperty(type=ChannelParams)
    green: bpy.props.CollectionProperty(type=ChannelParams)
    blue: bpy.props.CollectionProperty(type=ChannelParams)

def inv_lerp(v, min, max):
    return (v - min) / (max - min)

def clamp(v, min, max):
    ret = v if v > min else min
    ret = v if v < max else max
    return ret

class Prop():
    def __init__(self, name, min, max):
        self.min = min
        self.max = max
        if len(name) < 1:
            self.t = "num"
            self.value = 0.0
        elif str.isdigit(name[0]):
            self.t = "num"
            try:
                self.value = float(name)
            except:
                self.value = 0.0
        else:
            (n, d, s) = name.partition('.')
            if d != '.':
                self.t = "scalar"
                self.value = n
            elif n == "position":
                self.t = "position"
                self.value = s
            elif n == "normal":
                self.t = "normal"
                self.value = s
            else:
                self.t = "vector"
                self.value = n
                self.scalar = s

    def set_layer(self, verts):
        match self.t:
            case "scalar":
                self.layer = verts.layers.float.get(self.value)
            case "vector":
                self.layer = verts.layers.float_vector.get(self.value)
            case _:
                self.layer = None

    def get_data(self, vert):
        match self.t:
            case "num":
                return self.value
            case "position":
                match self.value:
                    case 'x':
                        return clamp(inv_lerp(vert.co[0], self.min, self.max), 0, 1)
                    case 'y':
                        return clamp(inv_lerp(vert.co[1], self.min, self.max), 0, 1)
                    case 'z':
                        return clamp(inv_lerp(vert.co[2], self.min, self.max), 0, 1)
            case "normal":
                match self.value:
                    case 'x':
                        return clamp(inv_lerp(vert.normal[0], self.min, self.max), 0, 1)
                    case 'y':
                        return clamp(inv_lerp(vert.normal[1], self.min, self.max), 0, 1)
                    case 'z':
                        return clamp(inv_lerp(vert.normal[2], self.min, self.max), 0, 1)
            case "scalar":
                return clamp(inv_lerp(vert[self.layer], self.min, self.max), 0, 1)
            case "vector":
                match self.s:
                    case 'x':
                        return clamp(inv_lerp(vert[self.layer][0], self.min, self.max), 0, 1)
                    case 'y':
                        return clamp(inv_lerp(vert[self.layer][1], self.min, self.max), 0, 1)
                    case 'z':
                        return clamp(inv_lerp(vert[self.layer][2], self.min, self.max), 0, 1)


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

    def flat_pixel_from_index(self, index, frame_count, cur_frame):
        pos = self.pixel_from_index(index, frame_count, cur_frame)
        pos = (pos[1] * self.width) + pos[0]
        return pos

    def frame_offset(self, frame_count):
        return self.y / frame_count

    def index_from_pos(self, pos):
        epsilon = 0.001
        x_index = (pos[0] - (self.x * 0.5)) / self.x
        y_index = pos[1] / self.y
        index = (self.width * math.floor(y_index)) + math.floor(x_index)
        return index if (x_index - math.floor(x_index) < epsilon) and (y_index - math.floor(y_index) < epsilon) else None
