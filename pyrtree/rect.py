import math

class Rect(object):
    """
    A rectangle class that stores: an axis aligned rectangle, and: two
     flags (swapped_x and swapped_y).  (The flags are stored
     implicitly via swaps in the order of minx/y and maxx/y.)
    """

    __slots__ = ("r", "swapped_x", "swapped_y")

    def __init__(self, minx,miny,maxx,maxy):
        self.swapped_x = (maxx < minx)
        self.swapped_y = (maxy < miny)
        
        x,y,xx,yy = minx,miny,maxx,maxy
        if self.swapped_x: x,xx = maxx,minx
        if self.swapped_y: y,yy = maxy,miny

        self.r = (x,y,xx,yy)




    def overlap(self, orect):
        return self.intersect(orect).area()

    def write_raw_coords(self, toarray, idx):
        x,y,xx,yy = self.r
        if (self.swapped_x):
            t = x
            x = xx
            xx = t
        if (self.swapped_y):
            t = y
            y = yy
            yy = t
        toarray[idx] = x
        toarray[idx+1] = y
        toarray[idx+2] = xx
        toarray[idx+3] = yy

    def area(self):
        if self.r is None: return 0
        x,y,x2,y2 = self.r
        w = x2 - x
        h = y2 - y
        return w * h

    def extent(self):
        x,y,xx,yy = self.r
        return (x,y,xx-x,yy-y)

    def grow(self, amt):
        x,y,x2,y2 = self.r
        a = amt * 0.5
        return Rect(x-a,y-a,x2+a,y2+a)

    def intersect(self,o):
        if self.r is None: return NullRect
        if o.r is None: return NullRect

        x,y,x2,y2 = self.r
        xx,yy,xx2,yy2 = o.r
        nx,ny = max(x,xx),max(y,yy)
        nx2,ny2 = min(x2,xx2),min(y2,yy2)
        w,h = nx2-nx, ny2-ny

        if w <= 0 or h <= 0: return NullRect

        return Rect(nx,ny,nx2,ny2)


    def does_contain(self,o):
        x,y,xx,yy = o.r
        return self.does_containpoint( (x,y) ) and self.does_containpoint( (xx,yy) )

    def does_intersect(self,o):
        return (self.intersect(o).area() > 0)

    def does_containpoint(self,p):
        x,y = p
        xx,yy,x2,y2 = self.r
        return (x >= xx and x <= x2 and y >= yy and y <= y2)

    def union(self,o):
        if o.r is None: return Rect(*self.r)
        if self.r is None: return Rect(*o.r)

        x,y,x2,y2 = self.r
        xx,yy,xx2,yy2 = o.r
        nx,ny = x if x < xx else xx, y if y < yy else yy
        nx2,ny2 = x2 if x2 > xx2 else xx2, y2 if y2 > yy2 else yy2
        res = Rect(nx,ny,nx2,ny2)
        assert(not res.swapped_x)
        assert(not res.swapped_y)
        return res
        
    def union_point(self,o):
        x,y = o
        return self.union(Rect(x,y,x,y))

    def diagonal_sq(self):
        if self.r is None: return 0
        x,y,w,h = self.r
        return w*w + h*h
    
    def diagonal(self):
        return math.sqrt(self.diagonal_sq())

NullRect = Rect(0.0,0.0,0.0,0.0)
NullRect.r = None
NullRect.swapped_x = False
NullRect.swapped_y = False

def union_all(kids):
    cur = NullRect
    for k in kids: cur = cur.union(k.rect)
    assert(False ==  cur.swapped_x)
    return cur
