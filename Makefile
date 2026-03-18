.PHONY: quality quality-lint quality-smoke reload-evm

QUALITY_SCRIPT := ./scripts/quality-check.sh
ODOO_CONTAINER := local-setup-docker-odoo-19-1
ODOO_RELOAD_CMD := odoo -c /etc/odoo/odoo.conf --db_host=db --db_port=5432 -r odoo -w odoo -d evm_dev --http-port=8074 --stop-after-init -u evm

quality:
	$(QUALITY_SCRIPT) all

quality-lint:
	$(QUALITY_SCRIPT) lint

quality-smoke:
	$(QUALITY_SCRIPT) smoke

reload-evm:
	docker restart $(ODOO_CONTAINER)
	docker exec $(ODOO_CONTAINER) sh -lc "$(ODOO_RELOAD_CMD)"
