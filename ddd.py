#!/usr/local/bin/python2.7
# encoding: utf-8

import sys
import os
import json
from argparse import ArgumentParser

from ddd.db import DB
from ddd.dataobjects.project import DddProject

def main():
    
    
    # Setup argument parser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help='Supported Subcommands',dest='subcommand')
    parser_c = subparsers.add_parser('check', help='Check the DDD Project for consistency')
    parser_c.add_argument(dest="dddfile", help="Filename of .ddd to add", metavar="dddfile", nargs='?')
    parser_c.add_argument('--config',help='Config file', nargs='?')
    parser_c.add_argument('--conditions',help='Condition Filename', nargs='?')
    
    parser_co = subparsers.add_parser('combine', help='Check the DDD Project for consistency')
    parser_co.add_argument(dest="dddfile", help="Filename of .ddd to add", metavar="dddfile", nargs='+')
    parser_co.add_argument('--config',help='Config file', nargs='?')
    parser_co.add_argument('--output',help='Output Filename', nargs='?')
    
    parser_v = subparsers.add_parser('view', help='Display the DDD Repository in a html page')
    parser_v.add_argument('--hash',help='Hash of the Object to check', nargs='?')
    parser_v.add_argument(dest='name', help='Name of the Object in the Index to check', nargs='?')
    
    parser_commit = subparsers.add_parser('commit', help='Commit the DDD Object(s) to a local repository')
    parser_commit.add_argument(dest="dddfile", help="Filename of .ddd to add", metavar="dddfile", nargs='?')
    parser_commit.add_argument('--message',dest='message', help='Commit Message', nargs='?')
    parser_commit.add_argument('--tag',dest='tag', help='Tag', nargs='?')
    
    parser_export = subparsers.add_parser('export', help='Commit the DDD Object(s) to a local repository')
    parser_export.add_argument('--template',dest='template',help='Export the source for the current project')
    parser_export.add_argument(dest='dddfile', help='Name of the Object to export', nargs='?')
    parser_export.add_argument('--config',help='Config file', nargs='?')
    parser_export.add_argument('--output',help='Output Filename', nargs='?')
    
    parser_init = subparsers.add_parser('init', help='Initialize Repository Folder Structure')
    
    # Process arguments
    args = parser.parse_args()
    
    
    db = DB('./repo')
    
    status = 0
    
    if args.subcommand=='check':
        data=db.open(args.dddfile)
        cond = {}
        if args.conditions:
            with open(args.conditions,'r')as fp:
                cond = json.load(fp)
        status=db.check(data,conditions=cond)
        return status
        
    elif args.subcommand=='combine':
        tmp = []
        for f in args.dddfile:
            tmp.append(db.open(f))
        
        c = db.open(args.config)
        proj = DddProject(components=tmp,config=c)
        db.dump(proj,args.output)
        
    elif args.subcommand=='view':
        db.view(name=args.name)
    elif args.subcommand=='commit':
        print args
        p = db.open(args.dddfile)
        db.commit_and_tag(p, args.tag, args.message)
    elif args.subcommand=='export':
        data=db.open(args.dddfile)
        if args.config:
            config=db.open(args.config)
        if args.template=='conditions.json':
            db.export_conditions(data, args.output)
        else:
            db.export_source(data=data,config=config, filename=args.output, template=args.template)
    elif args.subcommand=='init':
        for folder in ['index','objects','tags']:
            os.makedirs(os.path.join('./repo',folder))
    return status
    
if __name__ == "__main__":
    sys.exit(main())
    
    