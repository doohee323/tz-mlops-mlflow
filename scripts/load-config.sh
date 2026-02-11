#!/usr/bin/env bash
# Load config from /root/.k8s/ using prop function
# Source this in install scripts: source "$(dirname "${BASH_SOURCE[0]}")/../scripts/load-config.sh"

[[ -f /root/.bashrc ]] && source /root/.bashrc 2>/dev/null || true

# prop: read key from .k8s/{file}
# Search order: REPO_ROOT/.k8s/ (local), then /root/.k8s/ (fallback)
# Usage: prop 'project' 'project'   -> value of project= in [project] section
# Usage: prop 'project' 'domain'    -> value of domain= in [project] section
function prop {
  local key="${2}="
  local file
  if [[ -n "${REPO_ROOT}" ]] && [[ -f "${REPO_ROOT}/.k8s/${1}" ]]; then
    file="${REPO_ROOT}/.k8s/${1}"
  else
    file="/root/.k8s/${1}"
  fi
  local section="${3:-}"
  local rslt
  if [[ ! -f "$file" ]]; then
    echo ""
    return
  fi
  rslt=$(grep "${section}" "$file" -A 10 2>/dev/null | grep "$key" | head -n 1 | cut -d '=' -f2 | sed 's/ //g')
  [[ -z "$rslt" ]] && key="${2} = " && rslt=$(grep "${section}" "$file" -A 10 2>/dev/null | grep "$key" | head -n 1 | cut -d '=' -f2 | sed 's/ //g')
  rslt=$(echo "$rslt" | tr -d '\n' | tr -d '\r')
  echo "$rslt"
}
