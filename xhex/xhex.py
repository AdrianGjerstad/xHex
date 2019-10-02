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

  # Clear screen
  stdscr.clear()
  stdscr.refresh()

  prev_key = None

  for file in ARG_DATA['files']:
    while True:

      stdscr.refresh()
      prev_key = stdscr.getkey()

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
