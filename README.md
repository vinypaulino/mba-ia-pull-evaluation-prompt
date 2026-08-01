# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub (prompts de baixa qualidade)
2. **Refatorar e otimizar** esses prompts com técnicas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.8 (80%) em todas as métricas

---

## Técnicas Aplicadas (Fase 2)

| Técnica | Por quê | Como foi aplicada |
|---|---|---|
| **Few-shot Learning** (obrigatório) | Alinha formato, tom e granularidade com as referências do dataset | 3 exemplos de entrada/saída (UI simples, validação/API, multi-falha) |
| **Role Prompting** | Reduz respostas genéricas; ancora qualidade de PM | System prompt: Product Manager sênior |
| **Chain of Thought** | Bugs complexos exigem decomposição antes da story | 6 passos internos (ator → necessidade → benefício → ACs → edge cases → estrutura) |

### Exemplo prático (Few-shot + Role + CoT)

O `system_prompt` em `prompts/bug_to_user_story_v2.yml`:

1. Define a persona (**Role Prompting**).
2. Obriga raciocínio em etapas antes da resposta (**CoT**), sem expor o raciocínio.
3. Mostra 3 pares Entrada → Saída (**Few-shot**), incluindo bug complexo com seções `=== CRITÉRIOS DE ACEITAÇÃO ===`.
4. Separa responsabilidades: system = regras/exemplos; user = `{bug_report}`.

Arquivo: [`prompts/bug_to_user_story_v2.yml`](prompts/bug_to_user_story_v2.yml)

---

## Resultados Finais

**Status: APROVADO** — todas as métricas >= 0.8 (média 0.9033)

Provider usado na avaliação: `google` / `gemini-2.5-flash` (OpenAI sem quota no momento da execução).

### Links LangSmith

- Prompt público v2: https://smith.langchain.com/hub/viniciuspaulino/bug_to_user_story_v2
- Dataset de avaliação: `prompt-optimization-challenge-eval` (15 exemplos)
- Projeto: https://smith.langchain.com (workspace com `LANGSMITH_PROJECT=prompt-optimization-challenge`)

### Tabela comparativa (v1 vs v2)

| Métrica | v1 (ruim, ilustrativo) | v2 (otimizado, medido) | Meta |
|---|---:|---:|---:|
| Helpfulness | ~0.45 | **0.94** | >= 0.8 |
| Correctness | ~0.52 | **0.88** | >= 0.8 |
| F1-Score | ~0.48 | **0.81** | >= 0.8 |
| Clarity | ~0.50 | **0.94** | >= 0.8 |
| Precision | ~0.46 | **0.95** | >= 0.8 |
| Média | ~0.48 | **0.90** | >= 0.8 |

### Evidências da execução

```text
Prompt: viniciuspaulino/bug_to_user_story_v2

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.88 ✓

Métricas Base:
  - F1-Score: 0.81 ✓
  - Clarity: 0.94 ✓
  - Precision: 0.95 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.8
```

> Screenshots: capture no dashboard do LangSmith (prompt Hub + dataset `prompt-optimization-challenge-eval` + tracing de exemplos) e anexe na entrega/PR se o curso exigir.

---

## Como Executar

### Pré-requisitos

- Python 3.10–3.12 (recomendado 3.12; evite 3.14 — wheels quebram)
- Conta LangSmith + API key + handle do Hub (`USERNAME_LANGSMITH_HUB`)
- OpenAI e/ou Google Gemini API key

### Setup

```bash
cd mba-ia-pull-evaluation-prompt
python3.12 -m venv venv
source venv/bin/activate
pip install --index-url https://pypi.org/simple -r requirements.txt
cp .env.example .env
```

Preencha no `.env`:

```bash
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=prompt-optimization-challenge
USERNAME_LANGSMITH_HUB=seu_username_do_hub
OPENAI_API_KEY=...           # se LLM_PROVIDER=openai
GOOGLE_API_KEY=...           # se LLM_PROVIDER=google

# OpenAI (pago)
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# EVAL_MODEL=gpt-4o

# Gemini free (rate limit ~15 RPM — utils.py aplica pacing)
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
EVAL_MODEL=gemini-2.5-flash
```

### Ordem de execução

```bash
# 1) Pull do prompt ruim
python src/pull_prompts.py

# 2) Prompt otimizado em prompts/bug_to_user_story_v2.yml
#    (edite e itere se alguma métrica ficar < 0.8)

# 3) Push público ao Hub
python src/push_prompts.py

# 4) Avaliação (15 bugs × métricas LLM-as-judge; Gemini ~10 min)
python src/evaluate.py

# 5) Testes de validação do YAML
pytest tests/test_prompts.py -v
```

### Critério de aprovação

Todas as 5 métricas >= 0.8 **e** média >= 0.8.

---

## Estrutura do projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example
├── requirements.txt
├── README.md
├── prompts/
│   ├── bug_to_user_story_v1.yml
│   └── bug_to_user_story_v2.yml
├── datasets/
│   └── bug_to_user_story.jsonl
├── src/
│   ├── pull_prompts.py
│   ├── push_prompts.py
│   ├── evaluate.py
│   ├── metrics.py
│   └── utils.py
└── tests/
    └── test_prompts.py
```

**Implementado neste fork**

- `src/pull_prompts.py` — pull de `leonanluppi/bug_to_user_story_v1`
- `src/push_prompts.py` — push público de `{username}/bug_to_user_story_v2`
- `prompts/bug_to_user_story_v2.yml` — prompt otimizado (Few-shot + CoT + Role)
- `tests/test_prompts.py` — 6 testes de validação
- `src/utils.py` — pacing/retry leve para Gemini free tier (`LLM_MIN_INTERVAL_SEC`)

**Núcleo de avaliação (critérios/dataset):** não alterar a lógica de `evaluate.py`, `metrics.py` nem o `.jsonl`.
