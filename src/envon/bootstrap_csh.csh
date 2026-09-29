# envon managed bootstrap for csh/tcsh.
# This file is sourced by the shell rc (e.g. ~/.cshrc). It defines an
# "envon" alias that evaluates the activation command returned by envon.
#
# Usage (after `envon --install csh`):
#   source ~/.cshrc
#
# NOTE: The _envon_cmd variable must be set before sourcing this file.
# envon --install does this automatically in the generated managed file.

# Fallback for testing the file standalone
if (! $?_envon_cmd) then
    set _envon_cmd = "\envon"
endif

# Main alias:
# Extract first argument safely via sentinel array idiom to prevent subscript out of range.
# Non-activation commands (flags other than -d/--deactivate, or help) are executed directly.
# Activation/deactivation commands are evaluated in the current shell context.
alias envon 'set _envon_args = ( \!* "" ); if ( "$_envon_args[1]" == "--" ) set _envon_args = ( $_envon_args[2-] "" ); set _envon_info = 0; set _envon_deact_err = 0; set _envon_out = ""; if ( ( "$_envon_args[1]" == "-d" || "$_envon_args[1]" == "--deactivate" ) && ! $?VIRTUAL_ENV ) set _envon_deact_err = 1; if ( $_envon_deact_err == 1 ) echo "No virtual environment is currently active." > /dev/stderr; if ( $_envon_deact_err == 1 ) set _envon_ec = 1; if ( "$_envon_args[1]" =~ -* && "$_envon_args[1]" != "-d" && "$_envon_args[1]" != "--deactivate" || "$_envon_args[1]" == "help" ) set _envon_info = 1; if ( $_envon_info == 1 ) "$_envon_cmd" \!*; if ( $_envon_info == 1 ) set _envon_ec = $status; if ( $_envon_info == 0 && $_envon_deact_err == 0 ) set _envon_out = `"$_envon_cmd" --emit csh \!*`; if ( $_envon_info == 0 && $_envon_deact_err == 0 ) set _envon_ec = $status; if ( $_envon_info == 0 && $_envon_deact_err == 0 && $_envon_ec == 0 && "$_envon_out" != "" ) eval "$_envon_out"; eval "unset _envon_args _envon_info _envon_deact_err _envon_out _envon_ec; (exit $_envon_ec)"'
