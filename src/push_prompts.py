"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_FILE = Path("prompts/bug_to_user_story_v2.yml")
PROMPT_KEY = "bug_to_user_story_v2"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ("description", "system_prompt", "user_prompt", "version"):
        value = prompt_data.get(field, "")
        if not str(value).strip():
            errors.append(f"Campo obrigatório faltando ou vazio: {field}")

    system_prompt = prompt_data.get("system_prompt", "")
    if "[TODO]" in system_prompt or "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    if "{bug_report}" not in prompt_data.get("user_prompt", ""):
        errors.append("user_prompt deve conter a variável {bug_report}")

    techniques = prompt_data.get("techniques_applied", [])
    if not isinstance(techniques, list) or len(techniques) < 2:
        errors.append(
            f"Mínimo de 2 técnicas requeridas em techniques_applied, "
            f"encontradas: {len(techniques) if isinstance(techniques, list) else 0}"
        )

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return False

    full_name = f"{username}/{prompt_name}"
    system_prompt = prompt_data["system_prompt"]
    user_prompt = prompt_data["user_prompt"]

    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

    techniques = prompt_data.get("techniques_applied", [])
    tags = list(prompt_data.get("tags", []))
    for technique in techniques:
        if technique not in tags:
            tags.append(technique)

    description = prompt_data.get("description", "Prompt otimizado bug → user story")
    if techniques:
        description = f"{description} | Técnicas: {', '.join(techniques)}"

    print(f"Publicando prompt público: {full_name}")
    try:
        url = hub.push(
            full_name,
            chat_prompt,
            new_repo_is_public=True,
            new_repo_description=description,
            tags=tags,
        )
        print(f"✓ Push concluído: {url}")
        return True
    except Exception as e:
        print(f"❌ Erro no push: {e}")
        return False


def main():
    """Função principal"""
    os.chdir(Path(__file__).resolve().parent.parent)
    print_section_header("PUSH DE PROMPTS OTIMIZADOS")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    data = load_yaml(str(PROMPT_FILE))
    if not data or PROMPT_KEY not in data:
        print(f"❌ Prompt '{PROMPT_KEY}' não encontrado em {PROMPT_FILE}")
        return 1

    prompt_data = data[PROMPT_KEY]
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Validação OK")
    if not push_prompt_to_langsmith(PROMPT_KEY, prompt_data):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    print("\n✅ Push concluído.")
    print(f"   Hub: https://smith.langchain.com/hub/{username}/{PROMPT_KEY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
