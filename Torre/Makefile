# Makefile para comandos da TORRE

# Caminhos (relativos ao diretório atual)
CHECKPOINTS_DIR := checkpoints
LOGS_DIR := logs
REPORTS_DIR := reports
RELATORIOS_DIR := ../relatorios

.PHONY: torre_report torre_checkpoint torre_status torre_train torre_eval torre_list_checkpoints torre_list_logs torre_clean_logs torre_validate_dataset torre_help

# Gera relatório técnico de treino
torre_report:
	@echo "📊 Gerando relatório técnico da TORRE..."
	@python3 cli/generate_report.py
	@echo "✅ Relatório gerado em $(REPORTS_DIR)/train_summary.md"

# Cria checkpoint do estado atual
torre_checkpoint:
	@echo "💾 Criando checkpoint..."
	@python3 cli/create_checkpoint.py
	@echo "✅ Checkpoint criado em $(CHECKPOINTS_DIR)/"

# Atualiza status da TORRE
torre_status:
	@echo "📋 Atualizando status da TORRE..."
	@python3 cli/update_status.py
	@echo "✅ Status atualizado em $(RELATORIOS_DIR)/torre_status.json"

# Executa treino de uma fase
torre_train:
	@echo "🚀 Executando treino..."
	@echo "Uso: make torre_train PHASE=N [DATASET=path] [EPOCHS=N]"
	@if [ -z "$(PHASE)" ]; then \
		echo "❌ ERRO: Especifique PHASE (0-5)"; \
		exit 1; \
	fi
	@python3 cli/train.py --phase $(PHASE) \
		$$([ -n "$(DATASET)" ] && echo --dataset $(DATASET)) \
		$$([ -n "$(EPOCHS)" ] && echo --epochs $(EPOCHS))
	@echo "✅ Treino concluído"

# Avalia checkpoint
torre_eval:
	@echo "🔍 Avaliando checkpoint..."
	@echo "Uso: make torre_eval CHECKPOINT=path [DATASET=path]"
	@if [ -z "$(CHECKPOINT)" ]; then \
		echo "❌ ERRO: Especifique CHECKPOINT"; \
		exit 1; \
	fi
	@python3 cli/eval.py --checkpoint $(CHECKPOINT) \
		$$([ -n "$(DATASET)" ] && echo --dataset $(DATASET))
	@echo "✅ Avaliação concluída"

# Lista checkpoints disponíveis
torre_list_checkpoints:
	@echo "📦 Checkpoints disponíveis:"
	@ls -lh $(CHECKPOINTS_DIR)/*.ckpt 2>/dev/null || echo "Nenhum checkpoint encontrado"

# Lista logs disponíveis
torre_list_logs:
	@echo "📝 Logs disponíveis:"
	@ls -lh $(LOGS_DIR)/*.log 2>/dev/null || echo "Nenhum log encontrado"

# Limpa logs antigos (mantém últimos 30 dias)
torre_clean_logs:
	@echo "🧹 Limpando logs antigos (>30 dias)..."
	@find $(LOGS_DIR) -name "*.log" -mtime +30 -delete 2>/dev/null || true
	@echo "✅ Limpeza concluída"

# Valida conformidade constitucional dos datasets
torre_validate_dataset:
	@echo "🔒 Validando dataset..."
	@echo "Uso: make torre_validate_dataset DATASET=path"
	@if [ -z "$(DATASET)" ]; then \
		echo "❌ ERRO: Especifique DATASET"; \
		exit 1; \
	fi
	@python3 cli/validate_dataset.py --dataset $(DATASET)
	@echo "✅ Validação concluída"

# Help
torre_help:
	@echo "📚 Comandos disponíveis da TORRE:"
	@echo ""
	@echo "  make torre_report              - Gera relatório técnico (train_summary.md)"
	@echo "  make torre_checkpoint          - Cria checkpoint do estado atual"
	@echo "  make torre_status              - Atualiza status em relatorios/torre_status.json"
	@echo "  make torre_train PHASE=N       - Executa treino da fase N (0-5)"
	@echo "  make torre_eval CHECKPOINT=... - Avalia checkpoint"
	@echo "  make torre_list_checkpoints    - Lista checkpoints disponíveis"
	@echo "  make torre_list_logs           - Lista logs disponíveis"
	@echo "  make torre_clean_logs          - Limpa logs antigos (>30 dias)"
	@echo "  make torre_validate_dataset DATASET=... - Valida dataset"
	@echo ""
	@echo "📖 Ver curriculum/PLAN.md para detalhes do plano de treino"
