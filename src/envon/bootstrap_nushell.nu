# Deactivate the currently active Python virtual environment
def --env deactivate [] {
  if ("VIRTUAL_ENV" in $env) {
    let path_name = if "Path" in $env { "Path" } else { "PATH" }
    if ("_ENVON_PREV_PATH" in $env) {
      load-env { $path_name: $env._ENVON_PREV_PATH }
      hide-env _ENVON_PREV_PATH
    } else {
      let venv_dir = $env.VIRTUAL_ENV
      let bin_posix = ($venv_dir | path join "bin")
      let bin_win = ($venv_dir | path join "Scripts")
      let cur_path = ($env | get $path_name)
      let cleaned_path = ($cur_path | where {|p| ($p != $bin_posix) and ($p != $bin_win) and ($p != ($bin_posix | path expand)) and ($p != ($bin_win | path expand)) })
      load-env { $path_name: $cleaned_path }
    }
    hide-env VIRTUAL_ENV
    if ("VIRTUAL_ENV_PROMPT" in $env) {
      hide-env VIRTUAL_ENV_PROMPT
    }
    if ("_ENVON_OLD_PROMPT" in $env) {
      if ($env._ENVON_OLD_PROMPT | is-empty) {
        hide-env PROMPT_COMMAND
      } else {
        $env.PROMPT_COMMAND = $env._ENVON_OLD_PROMPT
      }
      hide-env _ENVON_OLD_PROMPT
    }
    $env.LAST_EXIT_CODE = 0
  } else {
    print -e "No virtual environment is currently active."
    $env.LAST_EXIT_CODE = 1
  }
}

# Activate or manage virtual environments with envon
def --wrapped --env envon [...args: string] {
  let effective_args = if ($args | is-empty) == false and ($args | first) == "--" {
    $args | skip 1
  } else {
    $args
  }

  # Handle help/info flags that don't need environment changes
  if ($effective_args | is-empty) == false {
    let first = ($effective_args | first)
    if ($first == '-d') or ($first == '--deactivate') {
      deactivate
      return
    }
    if ($first == 'help') or ($first == '-h') or ($first == '--help') or ($first == '--install') or ($first == '--print-path') or ($first == '--version') or ($first == '-V') or (($first | str starts-with '-') == true) {
      ^envon ...$effective_args
      return
    }
  }

  let raw_venv = try {
    ^envon --print-path ...$effective_args
  } catch { |e|
    $env.LAST_EXIT_CODE = ($e.exit_code? | default 1)
    return
  }

  let venv = ($raw_venv | str trim)
  if ($venv | is-empty) { return }

  let bin_posix = ($venv | path join 'bin')
  let bin_win = ($venv | path join 'Scripts')
  let bin_dir = if ($bin_posix | path exists) { $bin_posix } else if ($bin_win | path exists) { $bin_win } else { $bin_posix }

  if ("VIRTUAL_ENV" in $env) {
    deactivate
  }

  let path_name = if 'Path' in $env { 'Path' } else { 'PATH' }
  let old_path = ($env | get $path_name)
  let new_path = ($old_path | prepend ($bin_dir | path expand))
  let venv_name = ($venv | path basename)

  load-env {
    $path_name: $new_path,
    _ENVON_PREV_PATH: $old_path,
    VIRTUAL_ENV: ($venv | path expand),
    VIRTUAL_ENV_PROMPT: $venv_name
  }

  let disable_prompt = ("VIRTUAL_ENV_DISABLE_PROMPT" in $env) and ($env.VIRTUAL_ENV_DISABLE_PROMPT != "0") and ($env.VIRTUAL_ENV_DISABLE_PROMPT != "false")
  if not $disable_prompt {
    let virtual_prefix = $"\(($venv_name)\) "
    if not ("_ENVON_OLD_PROMPT" in $env) {
      if "PROMPT_COMMAND" in $env {
        let old_prompt = $env.PROMPT_COMMAND
        $env._ENVON_OLD_PROMPT = $old_prompt
        $env.PROMPT_COMMAND = if 'closure' in ($old_prompt | describe) {
          {|| $"($virtual_prefix)(do $old_prompt)" }
        } else {
          {|| $"($virtual_prefix)($old_prompt)" }
        }
      } else {
        $env._ENVON_OLD_PROMPT = ""
        $env.PROMPT_COMMAND = {|| $"($virtual_prefix)" }
      }
    }
  }

  $env.LAST_EXIT_CODE = 0
}
