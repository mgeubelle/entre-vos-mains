.PHONY: quality quality-lint quality-smoke

QUALITY_SCRIPT := ./scripts/quality-check.sh

quality:
	$(QUALITY_SCRIPT) all

quality-lint:
	$(QUALITY_SCRIPT) lint

quality-smoke:
	$(QUALITY_SCRIPT) smoke
