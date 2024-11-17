import numpy as np
import re

class Vector3:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def normalize(self):
        mag = np.sqrt(self.x**2 + self.y**2 + self.z**2)
        if mag > 0:
            self.x /= mag
            self.y /= mag
            self.z /= mag

def parse_planes(brush_data):
    planes = []
    
    for plane in brush_data:
        match = re.match(r'\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s*\)\s+\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s*\)\s+\(\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s*\)', plane)
        if match:
            p1 = Vector3(*map(float, match.groups()[0:3]))
            p2 = Vector3(*map(float, match.groups()[3:6]))
            p3 = Vector3(*map(float, match.groups()[6:9]))
            normal = (p2 - p1).cross(p3 - p1)
            normal.normalize()
            d = p1.dot(normal)
            planes.append((normal, d))

    #print(f"Parsed {len(planes)} planes")
    #for plane in planes:
    #    print(f"Plane normal: ({plane[0].x}, {plane[0].y}, {plane[0].z}), distance: {plane[1]}")
    
    return planes

def intersect_planes(p1, p2, p3):
    A = np.array([
        [p1[0].x, p1[0].y, p1[0].z],
        [p2[0].x, p2[0].y, p2[0].z],
        [p3[0].x, p3[0].y, p3[0].z]
    ])
    b = np.array([p1[1], p2[1], p3[1]])

    if np.linalg.matrix_rank(A) == 3:
        vertex = np.linalg.solve(A, b)
        return Vector3(*vertex)
    else:
        return None

def calculate_vertices(planes):
    vertices = []

    for i in range(len(planes)):
        for j in range(i + 1, len(planes)):
            for k in range(j + 1, len(planes)):
                vertex = intersect_planes(planes[i], planes[j], planes[k])
                if vertex and np.all(np.abs([vertex.x, vertex.y, vertex.z]) < 1e5):  # Filter out unrealistic vertices
                    vertices.append((vertex.x, vertex.y, vertex.z))
    
    #print(f"Calculated {len(vertices)} vertices")
    #for vertex in vertices:
    #    print(f"Vertex: ({vertex[0]}, {vertex[1]}, {vertex[2]})")
    
    return vertices
