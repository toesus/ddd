#!/usr/local/bin/python2.7
# encoding: utf-8

import sys
import os

from argparse import ArgumentParser

from ddd.db import DB


def main():
    
    
    # Setup argument parser
    parser = ArgumentParser()
    parser.add_argument("-c", "--check", dest="check", action="store_true", help="Check the DDD Project")
    parser.add_argument(dest="paths", help="Path to root folder of DDD Repository", metavar="path", nargs='+')

    # Process arguments
    args = parser.parse_args()
    
    paths = args.paths
    check = args.check
    db = DB()
    
    print "Load component from "+paths[0]
    #db.load('db/dumptest')
    db.load(paths[0])
    
    print "Loaded..."
    print ""
    
    for t in db.name_by_hash:
        print t + ':'
        for o in db.name_by_hash[t]:
            print o+' : '+db.name_by_hash[t][o]
            
if __name__ == "__main__":
    main()
    
    