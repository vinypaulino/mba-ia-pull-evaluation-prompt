"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = Path("prompts/bug_to_user_story_v1.yml")


def _extract_template(message_template) -> str:
    prompt = getattr(message_template, "prompt", None)
    if prompt is None:
        return ""
    return getattr(prompt, "template", "") or ""


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do Hub e salva em YAML local."""
    print_section_header("PULL DE PROMPTS DO LANGSMITH")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    print(f"Puxando prompt: {SOURCE_PROMPT}")
    try:
        prompt = hub.pull(SOURCE_PROMPT)
    except Exception as e:
        print(f"❌ Falha ao puxar prompt: {e}")
        return False

    system_prompt = ""
    user_prompt = "{bug_report}"

    for message in getattr(prompt, "messages", []):
        class_name = message.__class__.__name__.lower()
        template = _extract_template(message)
        if "system" in class_name:
            system_prompt = template
        elif "human" in class_name or "user" in class_name:
            user_prompt = template

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "created_at": str(date.today()),
            "tags": ["bug-analysis", "user-story", "product-management"],
            "source": SOURCE_PROMPT,
        }
    }

    if not save_yaml(data, str(OUTPUT_PATH)):
        return False

    print(f"✓ Prompt salvo em: {OUTPUT_PATH}")
    print(f"✓ Variáveis de input: {getattr(prompt, 'input_variables', [])}")
    return True


def main():
    """Função principal"""
    os.chdir(Path(__file__).resolve().parent.parent)
    ok = pull_prompts_from_langsmith()
    if ok:
        print("\n✅ Pull concluído com sucesso.")
        return 0
    print("\n❌ Pull falhou.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
