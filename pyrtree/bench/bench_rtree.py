
# TODO: path hackery.
if __name__ == "__main__":
    import sys, os
    mypath = os.path.dirname(sys.argv[0])
    sys.path.append(os.path.abspath(os.path.join(mypath, "../../")))

from pyrtree.rtree import RTree
from pyrtree.tests.test_rtree import RectangleGen,TstO

import time

# TODO: make these command-line params.

ITER=10000 # ten meeelion
INTERVAL=10 # log at every 10k

if __name__ == "__main__":
    G = RectangleGen()
    rt = RTree()
    start = time.clock()
    interval_start = time.clock()
    for v in range(ITER):
        if 0 == (v % INTERVAL):
            # interval time taken, total time taken, # rects, cur max depth
            t = time.clock()
            
            print("%d,%s,%f" % (v, "itime_t", t - interval_start))
            print("%d,%s,%d" % (v, "max_depth", rt.node.max_depth()))
            print("%d,%s,%d" % (v, "mean_depth", rt.node.mean_depth()))

            interval_start = time.clock()
        rt.insert(TstO(G.rect(0.000001)))

    # Done.
