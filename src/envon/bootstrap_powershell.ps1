function envon {
  param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
  $envonExe = Get-Command envon -CommandType Application -ErrorAction SilentlyContinue
  if (-not $envonExe) { Write-Error 'envon console script not found on PATH'; return }
  if ($Args.Count -gt 0) {
    if ($Args[0] -eq '--') { $Args = $Args[1..($Args.Count-1)] }
    elseif ($Args[0] -eq 'help' -or $Args[0] -eq '--help' -or $Args[0] -eq '--install' -or $Args[0].StartsWith('-')) {
      & $envonExe.Source @Args; return
    }
  }
  $cmd = & $envonExe.Source @Args
  if ($LASTEXITCODE -ne 0) { Write-Error $cmd; return }
  Invoke-Expression $cmd
}
