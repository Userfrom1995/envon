def --env envon [...args] {
  if ($args | is-empty) == false {
    let first = ($args | first)
    if $first == '--' { let args = ($args | skip 1); ^envon ...$args; return }
    if ($first == '-d') or ($first == '--deactivate') {
      # Handle deactivation
      let cmd = (^envon ...$args | str trim)
      if ($cmd | is-empty) == false {
        nu -c $cmd
      }
      return
    }
    if ($first == 'help') or ($first == '-h') or ($first == '--help') or ($first == '--install') or ($first == '--print-path') or (($first | str starts-with '-') == true) {
      ^envon ...$args; return
    }
  }
  let venv = (^envon --print-path ...$args | str trim)
  if ($venv | is-empty) { return }
  let act = ($venv | path join 'bin' 'activate.nu')
  if ($act | path exists) {
    echo $"overlay use '($act | path expand)'"
    echo 'Run the printed command in your interactive shell to activate the virtual environment.'
    return
  }
  echo 'Nushell activation script (activate.nu) not found for this virtual environment.'
  echo 'Create or upgrade the environment with a tool that generates Nushell activation scripts.'
}