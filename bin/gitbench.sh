#!/bin/sh

# Very quick'n'dirty.
# Automates some performance testing: 
#   working directory vs. last committed version.

ROOT=`dirname $0`/../

SCRATCH=$ROOT/scratch/

TEST_ITER=10000
TEST_INTERVAL=10

export TEST_ITER
export TEST_INTERVAL


python pyrtree/bench/bench_rtree.py > scratch/working.log

git stash save
python pyrtree/bench/bench_rtree.py > scratch/committed.log
git stash pop


python pyrtree/bench/bview.py scratch/committed.log scratch/working.log