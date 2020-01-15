from pyproj import Proj, transform

class ProjConvertor:
    def __init__(self, from_projection, to_projection, coordinate_x, coordinate_y):
        self.from_projection = from_projection
        self.to_projection = to_projection
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y

    def transform_projection(self):
        from_proj = Proj(self.from_projection)
        to_proj = Proj(self.to_projection)
        x, y = transform(from_proj, to_proj, self.coordinate_x, self.coordinate_y)
        return x, y