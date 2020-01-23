# -*- coding: utf-8 -*-

import pickle
from nlplib_pyknp2 import *
import re
import traceback
import sys
from knp_makedump import *


begin = int(sys.argv[1])
atype = int(sys.argv[2])
#begin=8100

# retty
if atype==1:
    data = makelist_retty(datafile="./resources/Rc_shaped.csv")
    makedumps_retty(data, begin=begin, num=100, dirname="dump_retty2", lines_split=True, debug=False)

# tabelog
elif atype==2:
    data = makelist_tabelog(datafile="./resources/Tc_shaped.csv")
    makedumps_tabelog(data, begin=begin, num=100, dirname="dump_tabelog", lines_split=True, debug=False)

# gurunabi
elif atype==3:
    data = makelist_gurunabi(datafile="./resources/Gc_shaped.csv")
    makedumps_gurunabi(data, begin=begin, num=100, dirname="dump_gurunabi", lines_split=True, debug=False)

#c = get_fromdump("dump_retty", 19998)
#c = get_fromdump("dump_tabelog", 299)
#c = get_fromdump("dump_gurunabi", 29)

#knp_analyze_from_commentlist_adj(c)
#knp_analyze_from_commentlist(c, print_result=True, visualize=False)