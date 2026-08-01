"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPTS_PATH = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def prompt_data():
    data = load_prompts(str(PROMPTS_PATH))
    assert data is not None, f"Não foi possível carregar {PROMPTS_PATH}"
    assert PROMPT_KEY in data, f"Chave '{PROMPT_KEY}' ausente no YAML"
    return data[PROMPT_KEY]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data
        assert isinstance(prompt_data["system_prompt"], str)
        assert prompt_data["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system = prompt_data["system_prompt"].lower()
        role_markers = ["você é", "product manager", "persona"]
        assert any(marker in system for marker in role_markers), (
            "system_prompt deve definir uma persona/role"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system = prompt_data["system_prompt"].lower()
        format_markers = [
            "como",
            "eu quero",
            "para que",
            "user story",
            "critérios de aceitação",
            "markdown",
        ]
        matches = sum(1 for marker in format_markers if marker in system)
        assert matches >= 2, "system_prompt deve exigir formato de User Story"

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system = prompt_data["system_prompt"].lower()
        few_shot_markers = ["exemplo", "entrada:", "saída:", "few-shot", "few shot"]
        assert any(marker in system for marker in few_shot_markers), (
            "system_prompt deve conter exemplos few-shot"
        )
        techniques = [t.lower() for t in prompt_data.get("techniques_applied", [])]
        assert "few-shot" in techniques or "few shot" in techniques

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        blob = "\n".join(
            [
                str(prompt_data.get("system_prompt", "")),
                str(prompt_data.get("user_prompt", "")),
                str(prompt_data.get("description", "")),
            ]
        )
        assert "[TODO]" not in blob
        assert "TODO" not in blob

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert isinstance(techniques, list)
        assert len(techniques) >= 2, (
            f"Esperado >= 2 técnicas, encontrado: {len(techniques)}"
        )
        is_valid, errors = validate_prompt_structure(prompt_data)
        assert is_valid, errors


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
