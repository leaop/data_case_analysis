# 📌 Mini-dicionário — Métricas Derivadas (Gold)

| Métrica | Tipo | Descrição (objetiva) |
|---|---:|---|
| processo_encerrado | 0/1 | Proxy de encerramento administrativo (situação/fase) |
| tipo_encerramento | texto | EM_ANDAMENTO / DEFERIDO / INDEFERIDO / ARQUIVADO / ENCERRADO_ADMIN |
| ano_encerramento | inteiro | Ano do encerramento (quando aplicável) |
| tempo_tramitacao_categoria | texto | Curto (≤1 ano) / Médio (1–2 anos) / Longo (>2 anos) |
| tempo_acima_mediana_global | 0/1 | 1 se tempo_tramitacao_dias > mediana global |
| tempo_padronizado_zscore | num | z-score do tempo de tramitação (outliers) |
| ato_sensivel_flag | 0/1 | 1 se ATO for sensível (autoriz./credenc./etc.) |
| flag_risco_alto | 0/1 | Proxy de risco alto (regras combinadas) |
| score_risco_regulatorio | 0–100 | Score ponderado (vagas/endereço/tempo/ato) |
| qtd_processos_por_ies | inteiro | Volume de processos associados à mesma IES |
| qtd_processos_por_curso | inteiro | Volume de processos associados ao mesmo curso |
| qtd_processos_por_area_cine | inteiro | Volume de processos por área CINE geral |
| processo_ativo | 0/1 | 1 se não encerrado |
| tempo_em_aberto_dias | inteiro | Dias desde o protocolo até hoje (somente ativos) |
| faixa_tempo_em_aberto | texto | Até 1 ano / 1–2 anos / +2 anos |
