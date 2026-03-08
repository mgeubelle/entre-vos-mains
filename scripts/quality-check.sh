#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${EVM_COMPOSE_FILE:-/home/mgeubelle/dev/odoo-scripts/local-setup-docker/docker-compose.yml}"
ODOO_SERVICE="${EVM_ODOO_SERVICE:-odoo-19}"
DB_SERVICE="${EVM_DB_SERVICE:-db}"
DB_HOST="${EVM_DB_HOST:-db}"
DB_NAME="${EVM_DB_NAME:-evm_dev}"
LINT_TARGET="${QUALITY_LINT_TARGET:-addons/evm}"
RUFF_VERSION="${RUFF_VERSION:-0.11.0}"

usage() {
  cat <<'EOF'
Usage: scripts/quality-check.sh [all|lint|smoke]

Environment overrides:
  EVM_COMPOSE_FILE   Docker Compose file for the shared Odoo stack
  EVM_ODOO_SERVICE   Odoo service name in the shared stack
  EVM_DB_SERVICE     PostgreSQL service name in the shared stack
  EVM_DB_HOST        PostgreSQL hostname seen from the Odoo container
  EVM_DB_NAME        Development database used for the smoke test
  QUALITY_LINT_TARGET Path checked by ruff
  RUFF_VERSION       Ruff version pinned by uvx
EOF
}

run_lint() {
  echo "==> Ruff lint: ${LINT_TARGET}"
  (
    cd "${ROOT_DIR}"
    uvx --from "ruff==${RUFF_VERSION}" ruff check "${LINT_TARGET}"
  )
}

db_exists() {
  docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
    psql -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" \
    | grep -qx '1'
}

run_smoke() {
  local install_args

  if db_exists; then
    install_args="-u evm"
    echo "==> Odoo smoke test: upgrade evm on ${DB_NAME}"
  else
    install_args="-i base,web,evm"
    echo "==> Odoo smoke test: initialize ${DB_NAME} and install evm"
  fi

  docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" sh -lc \
    "odoo -c /etc/odoo/odoo.conf --db_host=${DB_HOST} --db_port=5432 -r odoo -w odoo \
    -d ${DB_NAME} --http-port=8070 --stop-after-init ${install_args} --test-enable --test-tags /evm"
}

main() {
  local target="${1:-all}"

  case "${target}" in
    all)
      run_lint
      run_smoke
      ;;
    lint)
      run_lint
      ;;
    smoke)
      run_smoke
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
