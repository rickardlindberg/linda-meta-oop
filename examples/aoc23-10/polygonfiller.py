import sys

def print_polygon(width, height, polygon):
    for y in range(height):
        for x in range(width):
            sys.stdout.write(classify(polygon, x, y))
        sys.stdout.write("\n")

def classify(polygon, x, y):
    if (x, y) in polygon:
        return "O"
    elif hits_ede(polygon, x, y):
        return "#"
    inside_flag = False
    for kind, at, start, stop in yield_edges(polygon):
        if kind == "|" and at < x and start < y <= stop:
            inside_flag = not inside_flag
    if inside_flag:
        return "."
    else:
        return " "

def hits_ede(polygon, x, y):
    for kind, at, start, stop in yield_edges(polygon):
        if kind == "|" and x == at and start < y < stop:
            return True
        elif kind == "-" and y == at and start < x < stop:
            return True
    return False

def yield_edges(polygon):
    x1, y1 = polygon[-1]
    for x2, y2 in polygon:
        if x1 == x2:
            yield ("|", x1, min(y1, y2), max(y1, y2))
        else:
            assert y1 == y2
            yield ("-", y1, min(x1, x2), max(x1, x2))
        x1, y1 = x2, y2
    return False

if __name__ == "__main__":
    print_polygon(20, 20, [
        (5, 5),    (15, 5),
                   (15, 15),
        (5, 15),
    ])
    print_polygon(30, 20, [
        (5, 5),    (10, 5),
                   (10, 10), (15, 10),
                             (15, 15),
        (5, 15),
    ])
