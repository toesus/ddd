#!/usr/local/bin/python2.7
# encoding: utf-8

import sys
import os

from argparse import ArgumentParser

from ddd.db import DB


def main():
    
    
    # Setup argument parser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='Supported Subcommands',dest='subcommand')
    parser_c = subparsers.add_parser('check', help='Check the DDD Project for consistency')
    parser_v = subparsers.add_parser('view', help='Display the DDD Repository in a html page')
    parser_commit = subparsers.add_parser('commit', help='Commit the DDD Object(s) to a local repository')
    parser.add_argument(dest="paths", help="Path to root folder of DDD Repository", metavar="path", nargs='+')
    
    
    # Process arguments
    args = parser.parse_args()
    print str(args)
    
    paths = args.paths
    
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
    
    if args.subcommand=='check':
        db.check()
    elif args.subcommand=='view':
        db.view()
    elif args.subcommand=='commit':
        if db.check()==0:
            db.commit()
        else:
            print "Project is not consistent, committing not allowed"
            
if __name__ == "__main__":
    main()
    
    