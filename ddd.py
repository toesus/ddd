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
    parser_c.add_argument('--hash',help='Hash of the Object to check', nargs='?')
    parser_c.add_argument(dest='name', help='Name of the Object in the Index to check', nargs='?')
    parser_v = subparsers.add_parser('view', help='Display the DDD Repository in a html page')
    parser_commit = subparsers.add_parser('commit', help='Commit the DDD Object(s) to a local repository')
    parser_add = subparsers.add_parser('add', help='Add a component to the index of a local repository')
    parser_add.add_argument(dest="dddfile", help="Filename of .ddd to add", metavar="dddfile", nargs=1)
    
    parser.add_argument(dest="paths", help="Path to root folder of DDD Repository", metavar="path", nargs=1)
    
    parser_export = subparsers.add_parser('export', help='Commit the DDD Object(s) to a local repository')
    parser_export.add_argument('--source',dest='source',action='store_true',help='Export the source for the current project')
    
    # Process arguments
    args = parser.parse_args()
    print str(args)
    
    paths = args.paths
    
    print "Open repo "+paths[0]
    db = DB(paths[0])
    
    
    
    if args.subcommand=='add':
        print "Adding File "+args.dddfile[0]
        db.add(args.dddfile[0])
    elif args.subcommand=='check':
        if args.name:
            db.check(db.index.get(args.name).getHash())
    elif args.subcommand=='view':
        db.view()
    elif args.subcommand=='commit':
        if db.check(h)==0:
            db.commit()
        else:
            print "Project is not consistent, committing not allowed"
    elif args.subcommand=='export':
        if db.check(h)==0:
            if args.source:
                print "Exporting Source"
                db.export_source(h)
                
        else:
            print "Project is not consistent, exporting not allowed"
            
if __name__ == "__main__":
    main()
    
    