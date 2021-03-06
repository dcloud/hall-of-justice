#!/usr/bin/env python3

import os
import sys
import logging
import csv
import argparse
from signal import signal, SIGPIPE, SIG_DFL

logger = logging.getLogger()
signal(SIGPIPE, SIG_DFL)


def unidentified_states(item):
    value = item.get('State', None)
    return (value is None or (len(value) > 2 and value.strip() != "National"))


def no_title(item):
    value = item.get('Title', None)
    return value == '' or value is None


def no_group(item):
    value = item.get('Group name', None)
    return value == '' or value is None


def multiple_categories(item):
    value = item.get('Category', '')
    value_list = value.split(',')
    return (len(value_list) > 1)


FILTER_MAP = {
    'ufo-states': unidentified_states,
    'no-title': no_title,
    'no-group': no_group,
    'multi-cat': multiple_categories
}


def main(args):
    filter_name = getattr(args, 'filter', None)
    filter_func = FILTER_MAP.get(filter_name, None)

    columns = getattr(args, 'columns', None)

    reader = csv.DictReader(args.infile)
    fieldnames = reader.fieldnames
    filtered_items = filter(filter_func, reader) if filter_func else (r for r in reader)
    if columns:
        fieldnames = list(c for c in columns if c in fieldnames)
        filtered_items = (dict((f, row[f]) for f in fieldnames if f in row) for row in filtered_items)

    writer = csv.DictWriter(sys.stdout, fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for item in filtered_items:
        writer.writerow(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filters a CSV file using a custom set of predefined filters')
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help='Path to the CSV file to search on')
    parser.add_argument('--columns', type=str, nargs='+',
                        help='Column names to output')
    parser.add_argument('--filter', type=str,
                        choices=sorted(FILTER_MAP.keys()),
                        help='Specify a predefined filter to run on the CSV')
    args = parser.parse_args()
    main(args)
