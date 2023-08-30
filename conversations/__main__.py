#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: __main__.py (as part of project conversations)
#   Created: 28/04/2023 14:29
#   Last Modified: 28/04/2023 14:29
# -----------------------------------------------------------------------------
#   Author: William N. Havard
#           Postdoctoral Researcher
#
#   Mail  : william.havard@ens.fr / william.havard@gmail.com
#  
#   Institution: ENS / Laboratoire de Sciences Cognitives et Psycholinguistique
#
# ------------------------------------------------------------------------------
#   Description: 
#       • 
# -----------------------------------------------------------------------------

from conversations.conversation import Conversation

def main(**kwargs):
    pass


def _parse_args(argv):
    import argparse

    logging_levels = sorted(logging._levelToName.items(), key=lambda t: t[0], reverse=True)[:-1]

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('', help='')
    parser.add_argument('-v', '--verbosity', action="count", default=0,
                        help="Controls output verbosity. Critical and error messages will always be displayed. "
                             "({})".format(', '.join(['{}: {}'.format(level, '-' + 'v'*i_level)
                                           for i_level, (_, level) in enumerate(logging_levels[2:], 1)])))

    args = parser.parse_args(argv)
    args = vars(args)

    # Handle verbosity argument
    verbosity = min(args.pop('verbosity'), 3)
    verbosity = verbosity + 1 if verbosity > 0 else 1
    args['verbosity'] = logging_levels[verbosity][0]

    return args


if __name__ == '__main__':
    import sys
    import logging

    pgrm_name, argv = sys.argv[0], sys.argv[1:]
    args = _parse_args(argv)

    logging.basicConfig(level=args.pop('verbosity'))

    try:
        main(**args)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)
