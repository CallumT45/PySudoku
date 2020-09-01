class Line():
    def __init__(self, p1, p2):
        """
        Make sure p1 and p2 are diff
        """
        if p1[0] == p2[0]:
            p_temp = list(p1)
            p_temp[0] += 0.001
            p1 = tuple(p_temp)
        self.slope = (p2[1] - p1[1])/(p2[0] - p1[0])
        self.point = p1

    def findY(self, x):
        return self.slope*(x - self.point[0]) + self.point[1]

    def find_intersection(self, o):
        if (abs(o.slope - self.slope) < 0.5):
            return None

        x = (- self.slope*self.point[0] + self.point[1] +
             o.slope*o.point[0] - o.point[1])/(o.slope - self.slope)
        y = self.findY(x)
        return (round(x, 2), round(y, 2))

    def point_on_line(self, p):
        return abs(p[1] - self.findY(p[0])) < 0.05


if __name__ == "__main__":
    Line([100, 1000], [100, -1000])
