envon() {
  if [ "$#" -gt 0 ]; then
    case "$1" in
      help|-h|--help|--install|--print-path) command envon "$@"; return $? ;;
      -d|--deactivate) ;; # Allow these to be eval'd
      -*) command envon "$@"; return $? ;;
    esac
  fi
  cmd=$(command envon "$@"); ec=$?
  if [ $ec -ne 0 ]; then printf %s\n "$cmd" >&2; return $ec; fi
  eval "$cmd"
}
