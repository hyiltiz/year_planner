#! /usr/bin/env python3

__author__ = "Hörmet Yiltiz"
__copyright__ = "Copyright (C) 2021-2022 Hörmet Yiltiz"
__license__ = "GNU GPL version 3 or later"
__version__ = "0.1"

from os import popen
from sys import argv
from itertools import product, chain
from datetime import date
from re import compile

def year_planner(year: int = 2022):
    """Planner based on BSD ncal, requires backward compatibility mode of ncal
    provided by a patch in Debian."""
    syscall_str = f'ncal -Mwb {year}'
    cal = popen(syscall_str).read().splitlines()

    # fix the highlighted today
    today_marker = '_\x08'
    today = int(date.today().strftime('%d'))
    for i, ical in enumerate(cal):
        if today_marker in ical:
            cal[i] = cal[i].replace('_\x08', '{:2}'.format(today))

    
    newlines = [0]
    newlines += [i for i, x in enumerate(cal) if '' == x]
    newlines.append(len(cal)+1)
    # 0th line is year,
    # 1nd line is month names
    month_width = cal[2].index('w|', 2) - cal[2].index('w|', 1)
    if month_width != 27:
        print('WARNING: unusual ncal build parameters detected.')

    month_blocks = []
    # 12 months = 3x4
    for irow, icol in product(range(4), range(3)):
        block = [x[icol*month_width:(icol+1)*month_width] for i, x in enumerate(cal)
                    if newlines[irow] < i < newlines[irow + 1]]
        month_blocks.append(block)

    # clean up the redundancy, add month separators
    month_header_fmt = '{:' + f'{month_width}' + '}'
    month_pre_blank = '  | '  # to align with ' w| '
    month_sep = month_header_fmt.format('  | ')
    clean = []
    clean.append([month_blocks[0][1]]) # common week header
    for imonth in month_blocks:
        iresult = [month_sep]
        iresult += [month_header_fmt.format(month_pre_blank + imonth[0].strip() + f' {year}')]
        if imonth[-1].isspace():
            # last line is just space
            iresult += imonth[2:-1]
        else:
            iresult += imonth[2:]

        clean.append(iresult)
    clean_flat = list(chain(*clean))
    clean_flat = [x[0:-2] for x in clean_flat]

    # format into org
    org_fmt = '|{}|          |          |'
    org_header = '|{}| Plan     | Comment  |'.format(clean_flat[0])
    org_sep = compile('[a-zA-Z ]').sub('-', org_header)
    org_sep = org_sep.replace('|', '+')[1:-1]
    org_sep = f'|{org_sep}|'
    org_body = [org_fmt.format(x) for x in clean_flat[2:]]
    org_txt = [org_header] + [org_sep] + org_body

    org_file = f'year_planner_{year}.org'
    with open(org_file, 'w+') as f:
        f.writelines('\n'.join(org_txt))
        print(f'Saved {org_file}')

    return org_txt


if __name__ == '__main__':
    if len(argv) < 2:
        year = date.today().strftime('%Y')
    else:
        year = int(argv[1])
    year_planner(year)
