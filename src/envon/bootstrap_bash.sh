envon() {
  if [ "$#" -gt 0 ]; then
    case "$1" in
      --) shift ;; # Allow bare envon or args after '--' to be eval'd
      help|-h|--help|--install|--print-path|--version|-V) command envon "$@"; return $? ;;
      -d|--deactivate)
        if [ -z "$VIRTUAL_ENV" ]; then
          printf "No virtual environment is currently active.\n" >&2
          return 1
        fi
        ;;
      -*) command envon "$@"; return $? ;;
    esac
  fi
  local cmd ec
  cmd="$(command envon --emit bash "$@")"; ec=$?
  if [ $ec -ne 0 ]; then [ -n "$cmd" ] && printf "%s\n" "$cmd" >&2; return $ec; fi
  eval "$cmd"
}
