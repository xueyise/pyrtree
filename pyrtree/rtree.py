## R-tree.
# see doc/ref/r-tree-clustering-split-algo.pdf

MAXCHILDREN=10
MAX_KMEANS=5
import math, random, sys
EPSILON = 2.0 * sys.float_info.epsilon

class Rect(object):
    def __init__(self, b):
        self.r = b

    def overlap(self, orect):
        return self.intersect(orect).area()

    def area(self):
        if self.r is None: return 0
        x,y,w,h = self.r
        return w * h

    def bounds(self):
        x,y,w,h = self.r
        return (x,y,x+w,y+h)

    def grow(self, amt):
        x,y,w,h = self.r
        a = amt * 0.5
        return Rect((x-a,y-a,w+a,h+a))

    def intersect(self,o):
        if self.r is None: return NullRect
        if o.r is None: return NullRect

        x,y,x2,y2 = self.bounds()
        xx,yy,xx2,yy2 = o.bounds()
        nx,ny = max(x,xx),max(y,yy)
        nx2,ny2 = min(x2,xx2),min(y2,yy2)
        w,h = nx2-nx, ny2-ny

        if w <= 0 or h <= 0: return NullRect

        return Rect( (nx,ny,w,h ))


    def does_contain(self,o):
        x,y,xx,yy = o.bounds()
        return self.does_containpoint( (x,y) ) and self.does_containpoint( (xx,yy) )

    def does_intersect(self,o):
        return (self.intersect(o).area() > 0)

    def does_containpoint(self,p):
        x,y = p
        xx,yy,x2,y2 = self.bounds()
        xx,yy,x2,y2 = (xx - EPSILON), (yy - EPSILON), (x2 + EPSILON), (y2 + EPSILON)
        return (x >= xx and x <= x2 and y >= yy and y <= y2)

    def union(self,o):
        if o.r is None: return self
        if self.r is None: return o

        x,y,x2,y2 = self.bounds()
        xx,yy,xx2,yy2 = o.bounds()
        nx,ny = min(x,xx),min(y,yy)
        nx2,ny2 = max(x2,xx2),max(y2,yy2)
        return Rect( (nx,ny,nx2-nx,ny2-ny ))

    def union_point(self,o):
        x,y = o
        return self.union(Rect((x,y,0,0)))

    def diagonal(self):
        if self.r is None: return 0
        x,y,w,h = self.r
        return math.sqrt(w*w + h*h)

NullRect = Rect(None)


def union_all(kids):
    cur = NullRect
    for k in kids: cur = cur.union(k.rect)
    return cur

class RTree(object):
    def __init__(self):
        self.node = Node()
        self.node.parent = self
        self.count = 0

    def replace(self, o, ncs):
        self.node = Node(ncs,False)
        self.node.parent = self

    def insert(self,o):
        self.count += 1
        self.node.insert(o)

    def deleaf(self):
        pass
    

class Node(object):
    def __init__(self, kids = [], leaf=True, parent = None):
        self.children = kids
        for c in self.children: c.parent = self
        self.path=""
        self.parent = parent
        self.isleaf = leaf # isleaf <=> never overflowed.
        self.rect = union_all(self.children)

    def insert(self, x):
        if self.isleaf:
            self.__insert_child(x)
        else:
            # Find the child which needs the least area enlargement:
            ignored,child = min([ ((c.rect.union(x.rect)).area() - c.rect.area(),c) for c in self.children ])
            self.rect = self.rect.union(x.rect)
            child.insert(x)

    def query_rect(self, r):
        """ Return things that intersect with 'r'. """
        def p(o): return r.does_intersect(o.rect)
        for rr in self.walk(p):
            #if not isinstance(rr,Node):
            yield rr

    def query_point(self,point):
        """ Query by a point """
        def p(o): return o.rect.does_containpoint(point)
            
        for rr in self.walk(p):
            #if not isinstance(rr,Node):
            yield rr

    def walk(self, predicate):
        if predicate(self):
            yield self
            for c in self.children:
                for cr in c.walk(predicate):
                    yield cr


    def max_depth(self):
        if self.isleaf: return 1
        return 1 + (max([ s.max_depth() for s in self.children ]))

    def __insert_child(self, child):
        # Add it to the children:
        self.children.append(child)
        child.parent = self
        self.rect = union_all(self.children)
        
        if len(self.children) > MAXCHILDREN:
            self.overflow()
    
    def overflow(self):
        cur_score = -10
        cur_cluster = None
        clusterings = [ k_means_cluster(k,self.children) for k in range(2,MAX_KMEANS) ]
        score,bestcluster = max( [ (silhouette_coeff(c),c) for c in clusterings ])
        nodes = [ Node(c,self.isleaf,self.parent) for c in bestcluster if len(c) > 0]

        self.children = nodes
        self.isleaf = False
        self.parent.deleaf()

    def deleaf(self):
        if self.isleaf:
            self.isleaf = False
            self.children = [ Node([c], True, self) for c in self.children ]
            self.parent.deleaf()


def silhouette_w(node, cluster, next_closest_cluster):
    neighbors = [node.rect.union(r.rect).diagonal() for r in cluster ]
    strangers = [node.rect.union(s.rect).diagonal() for s in next_closest_cluster ]
    ndist = sum(neighbors) / len(neighbors)
    sdist = sum(strangers) / len(strangers)
    return (sdist - ndist) / max(sdist,ndist)

def silhouette_coeff(clustering):
    # special case for a clustering of 1.0
    if (len(clustering) == 1): return 1.0

    coeffs = []
    for cluster in clustering:
        others = [ c for c in clustering if c is not cluster ]
        others_cntr = [ center_of_gravity(c) for c in others ]
        ws = [ silhouette_w(node,cluster,others[closest(others_cntr,node)]) for node in cluster ]
        cluster_coeff = sum(ws) / len(ws)
        coeffs.append(cluster_coeff)
    return sum(coeffs) / len(coeffs)

def center_of_gravity(nodes):
    totarea = 0.0
    xs,ys = 0,0
    for n in nodes:
        if n.rect.r is not None:
            x,y,w,h = n.rect.r
            a = w*h
            xs = xs + (a * (x + (0.5 * w)))
            ys = ys + (a * (y + (0.5 * h)))
            totarea = totarea + a
    return (xs / totarea), (ys / totarea)

def closest(centroids, node):
    x,y = center_of_gravity([node])
    def d(c):
        xx,yy = c
        return math.sqrt(((xx-x) ** 2) + ((yy-y) ** 2))

    r_score,ridx = min( [ (d(c),i) for i,c in enumerate(centroids) ] )
    return ridx

def k_means_cluster(k, nodes):
    if len(nodes) <= k: return [ [n] for n in nodes ]
    
    ns = list(nodes)
    
    # Initialize: take n random nodes.
    random.shuffle(ns)

    cluster_starts = ns[:k]
    cluster_centers = [ center_of_gravity([n]) for n in ns[:k] ]
    
    
    # Loop until stable:
    while True:
        clusters = [ [] for c in cluster_centers ]
        
        for n in ns: 
            idx = closest(cluster_centers, n)
            clusters[idx].append(n)
        
        #FIXME HACK TODO: is it okay for there to be empty clusters?
        clusters = [ c for c in clusters if len(c) > 0 ]
        for c in clusters:
            if (len(c) == 0):
                print("Errorrr....")
                print("Nodes: %d, centers: %s" % (len(ns),
                                                              repr(cluster_centers)))

            assert(len(c) > 0)
            
        rest = ns
        first = False

        new_cluster_centers = [ center_of_gravity(c) for c in clusters ]
        if new_cluster_centers == cluster_centers : 
            return clusters
        else: cluster_centers = new_cluster_centers
        
    
    
