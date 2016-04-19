#!/usr/bin/env python

import sys
import time
import math
import random
import argparse
import itertools

import mss_finder


def arg_parser():
    parser = argparse.ArgumentParser(
        description="Find a magic square of cubes")
    parser.add_argument(
        '-v', '--verbose',
        action='store_true')
    parser.add_argument(
        '--skip-short-entries', action='store_true',
        default=False,
        help="Skip many possible solutions, only testing the most promising")
    return parser

def longrange(n):
    """Similar to xrange(n), but roll over to longs as needed"""

    i = 0
    while True:
        if i >= n:
            break
        else:
            yield i
        i += 1


class MSSGraphFinder(mss_finder.SquareSquareFinder):
    """
    Find Magic Square of Squares based on the graph
    properties of the square.
    """

    def __init__(self, skip_short_entries=False, verbose=False):
        self.skip_short_entries = skip_short_entries
        self.verbose = verbose
        self.cur_score = 0

    def find(self):
        def map_up(n):
            return (n+1)*(n+1)

        def show_sums(i, j, k, count, entry):
            print "%d+%d+%d = %d (%d matches): %r" % (
                k, j, i, k+j+i, count, entry)

        cur_max_sums = 0
        for i in itertools.count(0,1):
            s = map_up(i)
            #print i, s
            sums = {}
            for j,k in itertools.combinations(longrange(i), 2):
                k,j = (min((j,k)), max((j,k)))
                sj = map_up(j)
                sk = map_up(k)
                ssum = str(sj + sk + s)
                if not ssum in sums:
                    sums[ssum] = [(sk, sj, s)]
                    if cur_max_sums == 0:
                        show_sums(s, sj, sk, 1, sums[ssum])
                        cur_max_sums = 1
                else:
                    entry = sums[ssum]
                    entry.append((sk,sj,s))
                    count = len(entry)
                    if count > self.cur_score:
                        if count > cur_max_sums:
                            show_sums(s, sj, sk, count, entry)
                            cur_max_sums = count
                        elif self.skip_short_entries and count < cur_max_sums:
                            continue
                        elif self.verbose and count == cur_max_sums:
                            show_sums(s, sj, sk, count, entry)
                        if self.try_graph(entry, i, s):
                            return

    def is_magic(self, square, **kwargs):
        msquare = self.square_square(square)
        rows = [sum(msquare[r*3+c] for c in range(3)) for r in range(3)]
        cols = [sum(msquare[r*3+c] for r in range(3)) for c in range(3)]
        dia1 = sum(msquare[r*3+c] for r,c in ((0,0), (1,1), (2,2)))
        dia2 = sum(msquare[r*3+c] for r,c in ((0,2), (1,1), (2,0)))
        all_sums = rows+cols+[dia1, dia2]
        count = {k:0 for k in all_sums}
        for magic in all_sums:
            count[magic] += 1
        score = max(count.values())
        if score > self.cur_score:
            print "Candidate is new top-score with %d matches" % score
            self.print_sq(square)
            self.cur_score = score
        return(score == 8)

    def try_graph(self, start, count, vertex):
        def map_down(s):
            return [-1 if s == 0 else int(math.sqrt(ss))-1 for ss in s]

        self.max_value_width = 6
        possible = set(reduce(lambda x,y: x+y, [list(x) for x in start]))
        for sset in itertools.combinations(start, 3):
            if any(vertex not in s for s in sset):
                print "Failed to find %d in %r" % (vertex, sset)
                continue
            # Try each possible diagonal (not all perms because of symetry)
            for arrangement in ((0,1,2), (0,2,1), (2,1,0)):
                row = [i for i in sset[arrangement[0]] if i != vertex]
                col = [i for i in sset[arrangement[1]] if i != vertex]
                dia = [i for i in sset[arrangement[2]] if i != vertex]
                for r in itertools.permutations(row):
                    for c in itertools.permutations(col):
                        for d in itertools.permutations(dia):
                            square = [vertex, r[0], r[1], c[0], d[0], 0, c[1], 0, d[1]]
                            all = set(square)
                            rest = map_down(possible - all)
                            square = map_down(square)
                            #print "Trying:"
                            #self.print_sq(square)
                            for s1,s2 in itertools.permutations(rest, 2):
                                new_s = square[:]
                                new_s[5] = s1
                                new_s[7] = s2
                                if self.is_magic(new_s, quiet=False):
                                    self.print_sq(new_s)
                                    return True
        return False


def main():
    opts = arg_parser().parse_args()

    gf = MSSGraphFinder(skip_short_entries=opts.skip_short_entries, verbose=opts.verbose)
    gf.find()

if __name__ == '__main__':
    main()
