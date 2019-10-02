#!/usr/bin/env bash

function xhex() {
  command -v python3 > /dev/null

  if [[ $? -eq 1 ]]; then
    # Python3 Not Installed
    echo "xHex requires Python3 to run properly. Aborting."
    return 1
  fi

  if [[ ! $XHEXPATH == "/"* ]]; then
    if [[ $XHEXPATH == "" ]]; then
      echo "Environment variable \$XHEXPATH is not set. Aborting."
      return 1
    fi

    echo "Environment variable \$XHEXPATH is not an absolute path. Aborting."
    return 1
  fi

  if [[ ! -d $XHEXPATH ]]; then
    # XHEXPATH environment variable isn't valid.
    echo "Environment variable \$XHEXPATH does not point to a valid directory. Aborting."
    return 1
  fi

  # End of validation. Validation success
  if [[ $XHEXPATH == *"/" ]]; then
    python3 "${XHEXPATH}xhex.py" $@
    return $?
  fi

  python3 "${XHEXPATH}/xhex.py" $@
  return $?
}
