#!/usr/bin/env python3

########################################
# IMPORTS                              #
########################################

import sys
import traceback
import curses
import os

########################################
# CONSTANTS                            #
########################################

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

THEME_ERROR = '\033[31m\033[1m'
THEME_WARNING = '\033[33m\033[1m'
THEME_RESET = '\033[0m'

########################################
# CRAWL_ARGS                           #
########################################

def crawl_args(argc, args):
  global ARG_DATA
  ARG_DATA = {
    'files': []
  }

  argv = args.copy()

  skip_count = 0

  for i in range(1, argc):
    if skip_count > 0:
      skip_count -= 1
      continue

    argv[i] = argv[i].strip()

    if argv[i][0] == '-':
      argv[i] = argv[i][1:]
      if argv[i][0] == '-':
        argv[i] = argv[i][1:]
        if argv[i][0] == '-':
          sys.stderr.write('Cannot have more than 2 \'-\' characters before argument:\n')
          sys.stderr.write('--%s\n' % (argv[i]))
          return 1

        # Options with two '-'s
        if False:
          pass
        else:
          sys.stderr.write('Cannot recognize double-dashed option:\n')
          sys.stderr.write('--%s\n' % (argv[i]))
          return 1
        continue

      # Options with one '-'
      if False:
        pass
      else:
        sys.stderr.write('Cannot recognize single-dashed option:\n')
        sys.stderr.write('-%s\n' % (argv[i]))
        return 1
      continue

    # Arguments without '-'s
    if (argv[i][0] == '/' and os.path.isfile(argv[i])) or (argv[i][0] == '~' and os.path.isfile(os.environ['HOME'] + '/' + argv[i][1:])) or (os.path.isfile(os.environ['PWD'] + '/' + argv[i])):
      if argv[i][0] == '/':
        ARG_DATA['files'].append(argv[i])
      elif argv[i][0] == '~':
        ARG_DATA['files'].append(os.environ['HOME'] + '/' + argv[i][1:])
      else:
        ARG_DATA['files'].append(os.environ['PWD'] + '/' + argv[i])
    else:
      sys.stderr.write('Not a valid file: %s\n' % (argv[i]))
      return 1
    continue

  return 0

########################################
# SCREEN MANIPULATION                  #
########################################

def draw_bytes(b, yoff):
  global stdscr

  height, width = stdscr.getmaxyx()

  if yoff < 0: yoff = 0

  tx = len(hex(len(b))[2:])+2

  for i in range(16):
    stdscr.addstr(0, (i%16)*3+tx, hex(i)[2:].upper(), curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(0, tx+(16*3)+1+(i%16), hex(i)[2:].upper(), curses.color_pair(3) | curses.A_BOLD)

  for i in range(height-2):
    stdscr.addstr(i+1, 0, '0'*(tx-len(hex((i+yoff)*16)[2:])-2) + hex((i+yoff)*16)[2:].upper() + ':', (curses.color_pair(3) if (i+yoff) <= int(len(b)/16) else curses.color_pair(1)) | curses.A_BOLD)

  for i in range(height*16 - 32):
    if i+(yoff*16) >= len(b):
      stdscr.addstr(int(i/16)+1, (i%16)*3+tx, '00', curses.color_pair(1) | curses.A_BOLD)
      stdscr.addstr(int(i/16)+1, tx+(16*3)+1+(i%16), '.', curses.color_pair(1) | curses.A_BOLD)
      continue
    if int(b[i+(yoff*16)]) <= 32:
      stdscr.addstr(int(i/16)+1, tx+(16*3)+1+(i%16), '.')
    else:
      stdscr.addstr(int(i/16)+1, tx+(16*3)+1+(i%16), chr(b[i+(yoff*16)]))
    if len(hex(ord(chr(b[i+(yoff*16)])))[2:]) == 1:
      stdscr.addstr(int(i/16)+1, (i%16)*3+tx, '0' + hex(ord(chr(b[i+(yoff*16)])))[2:].upper())
      continue
    stdscr.addstr(int(i/16)+1, (i%16)*3+tx, hex(ord(chr(b[i+(yoff*16)])))[2:].upper())

  stdscr.refresh()

def overwrite_cmd(txt):
  global stdscr

  height, width = stdscr.getmaxyx()

  stdscr.addstr(height-1, 0, txt)
  stdscr.refresh()

########################################
# MAIN                                 #
########################################

def main(argc, argv):
  # Crawl Argument List
  tmp = crawl_args(argc, argv)
  if tmp == 1:
    return EXIT_FAILURE
  global ARG_DATA

  # Set up curses
  global stdscr
  stdscr = curses.initscr()
  curses.noecho()     # Disable echoing of keypresses to screen
  curses.cbreak()     # Send keypress event without pressing enter
  stdscr.keypad(True) # Enable directional arrows

  # Start colors
  curses.start_color()
  curses.use_default_colors()
  for i in range(0, curses.COLORS):
    curses.init_pair(i + 1, i, -1)

  # Clear screen
  stdscr.clear()
  stdscr.refresh()

  prev_key = None

  for file in ARG_DATA['files']:
    bytes_ = open(file, 'rb').read()
    draw_bytes(bytes_, 0)
    tx = len(hex(len(bytes_))[2:])+2
    stdscr.move(1, tx)
    stdscr.refresh()
    while True:
      key = stdscr.getkey()

      y, x = stdscr.getyx()
      if key == curses.KEY_LEFT:
        stdscr.move(y, x-1)
      elif key == curses.KEY_RIGHT:
        stdscr.move(y, x+1)
      elif key == curses.KEY_UP:
        stdscr.move(y-1, x)
      elif key == curses.KEY_DOWN:
        stdscr.move(y+1, x)

      stdscr.refresh()

  if len(ARG_DATA['files']) == 0:
    pass

  # Exit curses modes
  curses.nocbreak()
  stdscr.keypad(False)
  curses.echo()

  curses.endwin()

  # Return with success status code
  return EXIT_SUCCESS

# __main__ guard
if __name__ == '__main__':
  try:
    exit_code = main(len(sys.argv), sys.argv)
    if exit_code is None:
      sys.stderr.write('%sDEV WARNING%s: Returned from main without getting exit code. Exiting with code 255.\n' % (
        THEME_WARNING,
        THEME_RESET
      ))
      exit_code = 255
  except:
    global stdscr
    if stdscr is not None:
      # Exit curses modes
      curses.nocbreak()
      stdscr.keypad(False)
      curses.echo()

      curses.endwin()

    # Global error handler
    sys.stderr.write('\033[2J\033[H%sINTERNAL ERROR%s\n' % (THEME_ERROR, THEME_RESET))
    traceback.print_tb(sys.exc_info()[2])
    sys.stderr.write('%s%s' % (THEME_ERROR, sys.exc_info()[0].__name__))
    if str(sys.exc_info()[1]) != '':
      sys.stderr.write(': %s' % (str(sys.exc_info()[1])))
    sys.stderr.write(THEME_RESET)
    sys.stderr.write('\n')

    exit_code = 254

  sys.exit(exit_code)
else:
  raise InterruptedError('Cannot run xHex through another unknown script.')
