#!/bin/sh

# Very quick'n'dirty.
# Automates some performance testing: 
#   working directory vs. last committed version.

ROOT=`dirname $0`/../

SCRATCH=$ROOT/scratch/


python pyrtree/bench/bench_rtree.py > scratch/working.log

git stash save
python pyrtree/bench/bench_rtree.py > scratch/commited.log
git stash pop

python pyrtree/bench/bview.py scratch/committed.log scratch/working.log