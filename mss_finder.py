#!/usr/bin/env python

import sys
import time
import random
import argparse
import itertools


def arg_parser():
    parser = argparse.ArgumentParser(
        description="Find a magic square of cubes")
    parser.add_argument(
        '-v', '--verbose',
        action='store_true')
    parser.add_argument(
        '-s', '--step', metavar='N', type=int,
        default=9,
        help="The square root of the high value to start with")
    parser.add_argument(
        '-q', '--quiet',
        action='store_true', help="Be quiet")
    parser.add_argument(
        '-u', '--update', metavar='SECS',
        type=int, default=50,
        help="Status update frequency")
    parser.add_argument(
        '-r', '--random-combinations',
        action='store_true',
        help="Shuffle the combinations at each step for less predictable progress")
    parser.add_argument(
        '-m', '--min-root',
        type=int, default=1, metavar='N',
        help="Do not consider squares with a root less than this")
    parser.add_argument(
        '-t', '--tests',
        type=int, default=None, metavar='N',
        help="Number of checks to perform, default unlimited")
    return parser


class SquareSquareFinder(object):
    """
    A search tool for finding 3x3 magic squares
    whose values are all, themselves, squared.

    In other words, value 0 will be `n1^2`, value
    1 will be `n2^2` and so on.

    Whether this will ever complete is an open
    question...
    """

    # list of tuples of pairs of (location, rank)
    # where location is the location in the target
    # square numbered 0-8. The rank is the nth
    # element of the base combinatins being
    # considered. By restricting the first 2
    # or three values to these locations, we
    # avoid symetric redundancy.
    anchors = [
        ((0,0), (1,1)),
        ((0,0), (6,1)),
        ((0,1), (1,0)),
        ((0,1), (6,0)),
        ((0,0), (1,2), (4, 1)),
        ((0,0), (6,2), (4, 1)),
        ((0,2), (1,0), (4, 1)),
        ((0,2), (6,0), (4, 1)),
        ((0,1), (1,2), (4, 0)),
        ((0,1), (6,2), (4, 0)),
        ((0,2), (1,1), (4, 0)),
        ((0,2), (6,1), (4, 0)) ]

    # An empty square
    square = [0 for _ in range(9)]

    def __init__(self,
          min_root=1,
          random_combinations=False,
          update=60,
          quiet=True,
          verbose=False):
        self.min_root = min_root
        self.random_combinations = random_combinations
        self.update = update
        self.quiet = quiet
        self.verbose = verbose

    def find(self, step=9, max_tests=None):
        min_root = self.min_root
        start_t = time.time()
        last_t = start_t
        tests = 0
        self.seen_rows = False

        while True:
            print "At step %d" % step
            self.max_value_width = len(str(step*step))
            input_base = range(min_root-1, step-1)
            if self.random_combinations:
                random.shuffle(input_base)
            for base in itertools.combinations(input_base, 8):
                base = list(base) + [step-1]
                if self.random_combinations:
                    random.shuffle(base)
                for fixed in self.anchors:
                    new_base = base[len(fixed):]
                    new_corner = [base[f[1]] for f in fixed]
                    corner_locs = [f[0] for f in fixed]
                    if (len(fixed) == 2):
                        if 6 in corner_locs:
                            base_locs = [1,2,3,4,5,7,8]
                        else:
                            base_locs = [2,3,4,5,6,7,8]
                    else:
                        if 6 in corner_locs:
                            base_locs = [1,2,3,5,7,8]
                        else:
                            base_locs = [2,3,5,6,7,8]


                    for b_p in itertools.permutations(new_base):
                        square = self.square[:]
                        for ci in range(len(corner_locs)):
                            square[corner_locs[ci]] = new_corner[ci]
                        for bi in range(len(base_locs)):
                            square[base_locs[bi]] = b_p[bi]
                        tests += 1
                        now_t = time.time()
                        if not self.quiet and now_t - last_t >= self.update:
                            # Do more expensive validation when updating status
                            self.validate(square, step)
                            last_t = now_t
                            secs = int(now_t-start_t+0.5)
                            print "%d seconds in, after %d tests" % (secs, tests)
                            print "Current square is:"
                            self.print_sq(square)
                        if self.is_magic(square, self.quiet):
                            if not quiet:
                                print "After %d seconds:" % (now_t-start_t)
                                self.print_sq(square)
                            return self.square_square(square)
                        if self.verbose:
                            self.print_sq(list(new_corner) + list(b_p))
                        if max_tests and tests >= max_tests:
                            return None
            step += 1

    def validate(self, square, step):
        real_square = self.square_square(square)
        if any(v > step*step for v in real_square):
            print "Values are too large!"
            print "Max should be %d" % (step*step)
        seen = set([])
        for v in real_square:
            if v in seen:
                print "Duplicate value in square (are you Parker?): %d" % v
            seen.add(v)

    def square_square(self, s):
        return [ (i+1)*(i+1) for i in s ]

    def print_sq(self, sq):
        """
        Draw an ASCII-art picture of the square and its sums.
        """

        fmt_width = self.max_value_width+1
        fmt_value = "%%%dd" % (fmt_width)
        def map_sq(i):
            return fmt_value % i
        def indent_margin(c):
            return "".join(c for _ in range(fmt_width*3+4))
        s = self.square_square(sq)
        print " ", indent_margin(" "), "/=", sum((s[i] for i in (6,4,2)))
        for row_n in range(3):
            row  = [ s[row_n*3+i] for i in range(3) ]
            print " ", "  ".join(map(map_sq, row)), " =", sum(row)
        print " ", indent_margin("-"), "\=", sum((s[i] for i in (0,4,8)))
        print " ", "  ".join(map_sq(sum([s[r*3+col] for r in range(3)])) for col in range(3))
        print ""

    def is_magic(self, sq, quiet):
        s = self.square_square(sq)
        t = sum(s[i] for i in (0,1,2))
        if sum(s[i] for i in (3,4,5)) != t: return False
        if sum(s[i] for i in (6,7,8)) != t: return False
        if not self.quiet and not self.seen_rows:
            print "Rows work:"
            self.print_sq(sq)
            print "This is the last row-only update."
            self.seen_rows = True
        if sum(s[i] for i in (0,3,6)) != t: return False
        if sum(s[i] for i in (1,4,7)) != t: return False
        if sum(s[i] for i in (2,5,8)) != t: return False
        if not self.quiet:
            print "Rows+Cols work:"
            self.print_sq(sq)
        if sum(s[i] for i in (0,4,8)) != t: return False
        if not self.quiet:
            print "R+C+1diag works!:"
            self.print_sq(sq)
        if sum(s[i] for i in (6,4,2)) != t: return False
        return True

def main():
    opts = arg_parser().parse_args()

    step = opts.step
    start_t = time.time()
    last_t = start_t
    update_secs = opts.update
    min_root = opts.min_root

    if min_root < 1 or step - min_root < 7:
        print "--min-root must be no more than step-8"
        print "Step is %d, min_root is %d" % (step, min_root)
        sys.exit(1)

    sf = SquareSquareFinder(
        update=update_secs,
        min_root=min_root,
        quiet=opts.quiet,
        verbose=opts.verbose,
        random_combinations=opts.random_combinations)
    result = sf.find(step, max_tests=opts.tests)
    sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
