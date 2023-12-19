def countPointsInside(points):
    def addRangeInner(y, start, end):
        if y not in ranges:
            ranges[y] = []
        ranges[y].append((start, end))
    ranges = {}
    verticals = []
    x1, y1 = points[-1]
    for x2, y2 in points:
        if x1 == x2:
            start = min(y1, y2)
            end = max(y1, y2)
            verticals.append((x1, start, end))
            for y in range(start, end+1):
                addRangeInner(y, x1, x2)
        else:
            assert y1 == y2
            start = min(x1, x2)
            end = max(x1, x2)
            addRangeInner(y1, start, end)
        x1, y1 = x2, y2
    verticals = sorted(verticals, key=lambda x: x[0])
    for y in range(
        min(y for x, y in points),
        max(y for x, y in points)+1
    ):
        insideFlag = False
        last = None
        for at, start, stop in verticals:
            if start < y <= stop:
                if insideFlag:
                    addRangeInner(y, last+1, at-1)
                    last = None
                else:
                    last = at
                insideFlag = not insideFlag
        assert last is None
    count = 0
    for y, r in ranges.items():
        last = None
        for start, end in sorted(r, key=lambda x: x[0]):
            if y == SIZE:
                print(f"last = {last}")
            if last is None:
                count += addRange(y, start, end)
                last = end
            else:
                if end > last:
                    if start <= last:
                        start = last+1
                    count += addRange(y, start, end)
                    last = end
    return count

fills = []
points = [(0, 0)]
SIZE = 4

def addRange(y, start, end):
    if y == SIZE:
        print(f"range {start} -> {end}")
    for x in range(start, end+1):
        fills.append((x, y))
    return end - start + 1

def right():
    x, y = points[-1]
    points.append((x+SIZE, y))

def left():
    x, y = points[-1]
    points.append((x-SIZE, y))

def down():
    x, y = points[-1]
    points.append((x, y+SIZE))

def up():
    x, y = points[-1]
    points.append((x, y-SIZE))

#right()
#down()
#down()
#right()
#up()
#right()
#down()
#down()
#left()
#left()
#left()

right()
down()
left()

countPointsInside(points)

import sys

for y in range(0, max(y for x, y in fills)+1):
    for x in range(0, max(x for x, y in fills)+1):
        if (x, y) in fills:
            sys.stdout.write("#")
        else:
            sys.stdout.write(".")
    sys.stdout.write("\n")
