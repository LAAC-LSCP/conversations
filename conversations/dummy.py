#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: dummy.py (as part of project conversations)
#   Created: 28/04/2023 15:11
#   Last Modified: 28/04/2023 15:11
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
from pprint import pprint

from conversations.standards import register_user_function, argument, user_defined_functions, standard_filtering_rules

@register_user_function(
    argument('--bar')
)
def bar(foo):
    print(foo)

for func in user_defined_functions.items():
    print(func)

standard_filtering_rules()
