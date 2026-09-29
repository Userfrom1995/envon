function envon
    if test (count $argv) -gt 0
        set first $argv[1]
        if test "$first" = "--"
            set -e argv[1]
        else if test "$first" = "-d"; or test "$first" = "--deactivate"
            if not set -q VIRTUAL_ENV
                echo "No virtual environment is currently active." >&2
                return 1
            end
        else if string match -rq '^(help|-h|--help|--install|--print-path|--version|-V)' -- $first
            command envon $argv
            return $status
        else if string match -rq '^-' -- $first
            command envon $argv
            return $status
        end
    end
    set cmd (command envon --emit fish $argv)
    if test $status -ne 0
        test -n "$cmd"; and echo $cmd >&2
        return 1
    end
    eval $cmd
end
