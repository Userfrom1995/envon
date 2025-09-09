function envon
    if test (count $argv) -gt 0
        set first $argv[1]
        if test "$first" = "--"
            set -e argv[1]
        else if string match -rq '^(help|-h|--help|--install|-).*' -- $first
            command envon $argv
            return $status
        end
    end
    set cmd (command envon $argv)
    if test $status -ne 0
        echo $cmd >&2
        return 1
    end
    eval $cmd
end
