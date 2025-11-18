#!usr/bin/tcsh -f
#! /bin/tcsh -f
# envon wrapper script for tcsh compatibility

# Check if this is a help/install command
# alias envon 'if ( $#argv >= 1 ) then
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then
#         exec /usr/bin/envon $argv:q
#     endif
# endif

# # For environment activation
# set _ev=`~/.local/bin/envon $argv:q`
# if ( $status == 0 && "$_ev" != "" ) then
#     eval "$_ev"
# endif'

# alias envon `if ( $#argv >= 1 ) then
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then
#         exec /usr/bin/envon $argv:q
#     endif
# endif
# set _ev=`~/.local/bin/envon $argv:q`
# if ( $status == 0 && "$_ev" != "" ) then
#     eval "$_ev"
# endif`

# alias envon 'if ( $#argv >= 1 ) then \
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then \
#         ~/.local/bin/envon \!* \
#     else \
#         set _ev=`~/.local/bin/envon \!*` \
#         if ( $status == 0 && "$_ev" != "" ) then \
#             eval "$_ev" \
#         endif \
#         if ( $?_ev ) unset _ev \
#     endif \
# else \
#     set _ev=`~/.local/bin/envon` \
#     if ( $status == 0 && "$_ev" != "" ) then \
#         eval "$_ev" \
#     endif \
#     if ( $?_ev ) unset _ev \
# endif'
# For tcsh, we need to avoid complex control structures in aliases
# Instead, we'll use a very simple approach


# alias envon 'set _cmd="\!*"; if ( "$_cmd" == "--help" || "$_cmd" == "-h" || "$_cmd" == "help" || "$_cmd" == "--install" ) ~/.local/bin/envon \!*; if ( "$_cmd" != "--help" && "$_cmd" != "-h" && "$_cmd" != "help" && "$_cmd" != "--install" ) set _result="`~/.local/bin/envon \!*`" && if ( $status == 0 ) eval "$_result"; unset _cmd; if ( $?_result ) unset _result'

# alias envon 'if ( $#argv >= 1 ) then \
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then \
#         exec /.local/bin/envon $argv:q \
#     endif \
# endif \
# set _ev=`~/.local/bin/envon $argv:q` \
# if ( $status == 0 && "$_ev" != "" ) then \
#     eval "$_ev" \
# endif'

# alias envon `if ( $#argv >= 1 ) then
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then
#         exec /usr/bin/envon $argv:q
#     endif
# endif
# set _ev=`~/.local/bin/envon $argv:q`
# if ( $status == 0 && "$_ev" != "" ) then
#     eval "$_ev"
# endif`

# envon managed bootstrap - minimal fixes applied
# Define a shell function for envon
# alias envon 'envon_func \!*'

# envon_func:
#     if ( $#argv >= 1 ) then
#         if ("$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install") then
#             exec ~/.local/bin/envon $argv:q
#         endif
#     endif
#     set _ev=`~/.local/bin/envon $argv:q`
#     if ( $status == 0 && "$_ev" != "" ) then
#         eval "$_ev"
#     endif
#     return

#!/bin/tcsh -f
# envon wrapper script for tcsh

# Check if this is a help/install command
# if ( $#argv >= 1 ) then
#     if ( "$argv[1]" == "help" || "$argv[1]" == "-h" || "$argv[1]" == "--help" || "$argv[1]" == "--install" ) then
#         exec ~/.local/bin/envon $argv:q
#     endif
# endif

# # For environment activation
# set _ev=`~/.local/bin/envon $argv:q`
# if ( $status == 0 && "$_ev" != "" ) then
#     eval "$_ev"
# endif
alias envon '~/.local/bin/envon \!*'