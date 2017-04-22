import argparse
import json
import os
import re
import sys

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

DESCRIPTION = 'A limited alternative to jq with a simpler interface.'
ADDITIONAL_INFORMATION = 'The command line options depend upon your data source (or --spec-file). Provide sample data when running --help to see source specific options.'


def build_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION + ADDITIONAL_INFORMATION, add_help=False)
    # Read a line before printing help so we can include additional options
    parser.add_argument('--help', action='store_true', help='Show help output')
    parser.add_argument('--spec-file', type=str, help='Read specification of json from this file rather than guessing. If this file does not exist create it. This protects one against format changes causing crashes.')
    return parser

class FormatGuesser(object):
    def __init__(self, parser, argv):
        self.spec_file = None
        self.guessed = False
        self.parser = parser
        self.keys = None
        self.argv = argv
        self.parsed_args = None

    def set_spec_file(self, spec_file):
        self.spec_file = spec_file
        if os.path.exists(self.spec_file):
            with open(self.spec_file) as stream:
                self.keys = json.load(stream)
                add_specific_options(self.parser, self.keys)
                self.parsed_args = self.parser.parse_args(self.argv[1:])
            self.guessed = True

    def set_record(self, record):
        if not self.guessed:
            self.keys = list(record.keys())
            add_specific_options(self.parser, record.keys())
            self._maybe_write_spec(record)
            self.guessed = True
            self.parsed_args = self.parser.parse_args(self.argv[1:])
        return self.parsed_args

    def _maybe_write_spec(self, record):
        if self.spec_file and not os.path.exists(self.spec_file):
            write_spec_file(self.spec_file, record.keys())
            sys.exit()

    def attempt_show_help(self):
        if self.guessed:
            self.parser.print_help()
            sys.exit()


def main():
    parser = build_parser()
    args, _ = parser.parse_known_args()

    guesser = FormatGuesser(parser, sys.argv)
    if args.spec_file is not None:
        guesser.set_spec_file(args.spec_file)
    if args.help:
        guesser.attempt_show_help()

    while True:
        line = sys.stdin.readline()
        if line == '':
            break
        record = json.loads(line)
        args = guesser.set_record(record)

        if args.help:
            guesser.attempt_show_help()

        if filter_record(args, record):
            print json.dumps(record)

    guesser.parser.print_help()

def filter_record(args, record):
    for key in record:
        regular_expression = getattr(args, key + '_regexp', None)
        if (regular_expression is not None and
                not re.match(regular_expression, str(record[key]))):
            return False
    else:
        return True


def add_specific_options(parser, keys):
    "Add options specific to this json format"
    for key in keys:
        parser.add_argument('--' + key, type=str, help='Regular expression to match for this {}'.format(key), dest=key + '_regexp')

def write_spec_file(spec_file, keys):
    with open(spec_file, 'w') as stream:
        stream.write(json.dumps(keys))
