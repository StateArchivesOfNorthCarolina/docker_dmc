#!/usr/bin/env python
######################################################################
## $Revision: 1.1 $
## $Date: 2015/07/15 12:24:41 $
## Author: Carl Schaefer, Smithsonian Institution Archives 
######################################################################

import time
import os
import re


EOL = os.linesep

CHARACTER_SET = 'utf8'
# python does not recognize 'latin1'
# mysql does not recognize 'iso-8859-1'
#CHARACTER_SET = 'iso-8859-1'   # latin1

ALLOW_WRAP_CHOICE       = False
ALLOW_ALLOCATION_CHOICE = False
ALLOCATE_BY_DISPOSITION = -1

NOW         = time.time()
DAY_SECONDS = 24*60*60
DEFAULT_LAG = DAY_SECONDS * 31

month2num = {
   'Jan' : 1,
   'Feb' : 2,
   'Mar' : 3,
   'Apr' : 4,
   'May' : 5,
   'Jun' : 6,
   'Jul' : 7,
   'Aug' : 8,
   'Sep' : 9,
   'Oct' : 10,
   'Nov' : 11,
   'Dec' : 12
}

illegal_ascii_pat = re.compile('.*([\000-\010]|[\013-\014]|[\016-\037])', re.DOTALL)
# illegal decimal values: 0-8, 11-12, 14-31
illegal_ascii = set()
for a in range(9):
  illegal_ascii.add(a)
for a in (11, 12):
  illegal_ascii.add(a)
for a in range(14, 32):
  illegal_ascii.add(a)

######################################################################
def YMD (seconds):
  return time.strftime('%Y-%m-%d', time.localtime(seconds))

######################################################################
def MonthOf (seconds):
  return time.strftime('%m', time.localtime(seconds))

######################################################################
def YearOf (seconds):
  return time.strftime('%Y', time.localtime(seconds))

######################################################################
TODAY       = time.strftime('%Y-%m-%d', time.localtime(NOW))

######################################################################
def strict_datetime (s):
  (dt, zoffset) = mail_date2datetime(s)
  (d, t) = re.split(' ', dt)
  m = re.match('([+\-])([0-9]{2})([0-9]{2})$', zoffset)
  if m:
    zoffset = m.group(1) + m.group(2) + ':' + m.group(3)
  return d + 'T' + t + zoffset

######################################################################
def mail_date2datetime (d):
  if not d:
    return ('0000-00-00 00:00:00')

  exp = \
        '([^0-9]+)?' + \
        '(\d+)' + \
        '[^a-zA-Z]+' \
        '([a-zA-Z]+) ' + \
        '(\d{4}).+' + \
        '(\d\d:\d\d(:\d\d))[^0-9\-+]+' + \
        '([\-+]\d\d:?\d\d)?'
  m = re.match(exp, d)
  if m:
    day    = m.group(2)
    month  = m.group(3)
    if month in month2num.keys():
      month = month2num[month]
    else:
      month = '0'
    year   = m.group(4)
    time   = m.group(5)
    offset = m.group(7)
    if not offset:
      offset = ''
    return (year + '-' + "{:02d}".format(int(month)) + \
        '-' "{:02d}".format(int(day)) + 'T' + time, '{}:{}'.format(offset[0:3], offset[3:]))
  else:
    return ('0000-00-00 00:00:00')