from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/generated/extracted-text/jeremias.json"
QUESTIONS = ROOT / "data/questions.json"
PROMPT = ROOT / "ai_pipeline/prompts/01_extract_candidate_evidence.md"
OUTPUT = ROOT / "data/generated/evidence/jeremias.generated.json"
AUDIT = ROOT / "data/generated/evidence/jeremias.generation-audit.json"
REPORT = ROOT / "docs/pilot-evidence-jeremias.md"
PROMPT_VERSION = "extract-evidence-v1.0.0"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))).strip("-")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    allowed = [item["theme"] for item in json.loads(QUESTIONS.read_text(encoding="utf-8"))]
    pages = {page["page_number"]: page["text"] for page in source["pages"]}
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    items = []

    def add(theme, subtheme, level, page, start, end, summary, action, target, limitations):
        text = pages[page]; begin = text.find(start); finish = text.find(end, begin)
        if begin < 0 or finish < 0: raise ValueError(f"Trecho não localizado na página {page}: {start!r} / {end!r}")
        items.append({"theme": theme, "subtheme": subtheme, "evidence_level": level, "page": page,
                      "original_excerpt": text[begin:finish + len(end)], "neutral_summary": summary,
                      "proposed_action": action, "target_population": target, "limitations": limitations})

    # Saúde pública
    add("Saúde pública", "Hospitais", 3, 2, "• Construção de um novo Hospital Evangélico", "turistas;",
        "Propõe construir um Hospital Evangélico para atender população e turistas.", "Construir o hospital indicado.",
        "População pernambucana e turistas.", ["Não há localização, capacidade, prazo, orçamento ou modelo de gestão."])
    add("Saúde pública", "Saúde da pessoa idosa", 3, 2, "• Implantação de Hospital especializado", "idosa;",
        "Propõe implantar hospital especializado no atendimento à pessoa idosa.", "Implantar hospital especializado.",
        "Pessoas idosas.", ["Não há localização, capacidade, prazo, orçamento ou modelo de gestão."])
    add("Saúde pública", "Saúde digital", 3, 2, "• Informatização completa", "telemedicina;",
        "Propõe informatizar a rede, integrar prontuários e ampliar telemedicina.", "Executar a estratégia integrada de saúde digital descrita.",
        "Usuários e unidades da rede estadual de saúde.", ["Não há prazo, cobertura, padrões técnicos ou orçamento."])
    add("Saúde pública", "Atenção e prevenção", 2, 2, "• Fortalecimento da atenção básica", "programas preventivos;",
        "Propõe fortalecer atenção básica e ampliar programas preventivos.", "Fortalecer e ampliar os serviços mencionados.",
        "Não especificado no trecho.", ["Público prioritário, metas, prazo, recursos e forma de execução não são especificados."])
    add("Saúde pública", "Tecnologia e qualidade de vida", 2, 2, "• Prioridade para investimentos", "qualidade de vida.",
        "Propõe priorizar tecnologia médica e manter programas de promoção da qualidade de vida.", "Investir em tecnologia médica e promover qualidade de vida.",
        "Não especificado no trecho.", ["O trecho reúne ações transversais sem detalhar integração, público, metas, prazo ou recursos."])

    # Educação
    add("Educação", "Escolas militares", 2, 2, "• Ampliação e construção de Escolas Militares;", "Escolas Militares;",
        "Propõe ampliar e construir escolas militares.", "Ampliar e construir escolas militares.", "Estudantes; público específico não detalhado.",
        ["Não há quantidade, localização, prazo, orçamento ou modelo pedagógico."])
    add("Educação", "Progressão escolar", 2, 2, "• Revisão do modelo de progressão automática", "efetiva;",
        "Propõe revisar o modelo de progressão automática para assegurar aprendizagem.", "Revisar o modelo de progressão automática.",
        "Estudantes sujeitos ao modelo; etapa de ensino não especificada.", ["Não há critérios, processo, prazo ou indicadores."])
    add("Educação", "Valorização docente", 3, 2, "• Valorização salarial", "desempenho;",
        "Propõe valorização salarial, mais planejamento pedagógico e bonificação por desempenho.", "Executar a estratégia de valorização docente descrita.",
        "Professores.", ["O trecho possui caráter transversal e não informa valores, critérios de desempenho, metas ou prazo."])
    add("Educação", "Ensino técnico", 2, 2, "• Expansão das Escolas Técnicas Estaduais;", "Escolas Técnicas Estaduais;",
        "Propõe expandir as Escolas Técnicas Estaduais.", "Expandir a rede de escolas técnicas estaduais.", "Estudantes; público específico não detalhado.",
        ["Não há quantidade, localização, vagas, prazo ou orçamento."])
    add("Educação", "Robótica e inteligência artificial", 3, 2, "• Criação do Instituto Estadual", "Artificial;",
        "Propõe criar Instituto Estadual de Robótica e Inteligência Artificial.", "Criar o instituto indicado.", "Não especificado no trecho.",
        ["Não há público, atribuições, localização, prazo, orçamento ou forma de execução."])
    add("Educação", "Empreendedorismo e aprendizagem", 3, 2, "• Inserção do empreendedorismo", "empresas;",
        "Propõe inserir empreendedorismo na educação básica e criar Jovem Aprendiz em parceria com empresas.", "Executar as ações educacionais e de aprendizagem descritas.",
        "Estudantes da educação básica e jovens aprendizes.", ["O trecho reúne ações relacionadas, mas não informa currículo, parceiros, vagas, metas ou prazo."])

    # Segurança pública
    add("Segurança pública", "Efetivo", 3, 3, "• Contratação de novos policiais", "bombeiros;",
        "Propõe contratar policiais militares, civis e bombeiros.", "Realizar as contratações indicadas.", "Policiais militares, civis e bombeiros; beneficiários finais não especificados.",
        ["Não há quantidade, concurso, prazo, lotação ou orçamento."])
    add("Segurança pública", "Equipamentos e tecnologia", 3, 3, "• Modernização dos equipamentos", "inteligência artificial;",
        "Propõe modernizar equipamentos e ampliar drones, monitoramento eletrônico e inteligência artificial.", "Modernizar equipamentos e ampliar tecnologias de segurança.",
        "Forças de segurança.", ["O trecho forma uma estratégia tecnológica, mas não informa equipamentos, cobertura, salvaguardas, prazo ou orçamento."])
    add("Segurança pública", "Investigações", 3, 3, "• Redução do estoque de inquéritos", "anos;",
        "Propõe reduzir o estoque de inquéritos e processos investigativos em até três anos.", "Reduzir o estoque investigativo no prazo indicado.",
        "Não especificado no trecho.", ["Não há percentual, quantidade inicial, órgão responsável ou método."])
    add("Segurança pública", "Polícia Científica", 2, 3, "• Fortalecimento da Polícia Científica;", "Polícia Científica;",
        "Propõe fortalecer a Polícia Científica.", "Fortalecer a Polícia Científica.", "Polícia Científica; beneficiários finais não especificados.",
        ["Não há ação operacional, meta, prazo ou recursos."])
    add("Segurança pública", "Presença territorial", 3, 3, "• Ampliação da presença policial", "Estado;",
        "Propõe ampliar presença policial em todas as regiões do estado.", "Ampliar presença policial territorialmente.", "População de todas as regiões do estado.",
        ["Não há efetivo, unidades, prioridades, prazo ou orçamento."])
    add("Segurança pública", "Integração tecnológica", 3, 3, "• Implantação do Programa Pindorama", "pública.",
        "Propõe implantar o Programa Pindorama para integração tecnológica da segurança pública.", "Implantar o programa mencionado.", "Sistema de segurança pública; público final não especificado.",
        ["Não há descrição do programa, órgãos integrados, prazo, orçamento ou governança."])

    # Mobilidade e transporte
    add("Mobilidade e transporte", "Mobilidade cicloviária", 3, 5, "• Incentivo ao uso da bicicleta", "malha cicloviária;",
        "Propõe incentivar bicicleta e expandir malha cicloviária.", "Incentivar o modal e expandir sua infraestrutura.", "Usuários de bicicleta em todo o estado.",
        ["Não há extensão, localidades, prazo, segurança viária ou orçamento."])
    add("Mobilidade e transporte", "Transporte público", 2, 5, "• Modernização do transporte público;", "transporte público;",
        "Propõe modernizar o transporte público.", "Modernizar o transporte público.", "Usuários do transporte público.",
        ["Não há modelo de gestão, tecnologia, tarifa, meta, prazo ou orçamento."])
    add("Mobilidade e transporte", "Transporte alternativo", 2, 5, "• Apoio ao transporte alternativo regulamentado;", "regulamentado;",
        "Propõe apoiar transporte alternativo regulamentado.", "Apoiar a modalidade indicada.", "Operadores e usuários do transporte alternativo regulamentado.",
        ["Não há modalidade, regra, instrumento de apoio, prazo ou abrangência."])
    add("Mobilidade e transporte", "Mobilidade urbana e rural", 2, 5, "• Investimentos na mobilidade urbana e rural.", "rural.",
        "Propõe investimentos em mobilidade urbana e rural.", "Investir em mobilidade urbana e rural.", "Populações urbanas e rurais.",
        ["Não há ação específica, projeto, meta, prazo, território ou orçamento."])

    # Emprego e renda
    add("Emprego e renda", "Desenvolvimento regional", 3, 4, "• Implantação do Programa Pindorama", "regional;",
        "Propõe implantar o Programa Pindorama para desenvolvimento regional.", "Implantar o programa citado.", "Regiões do estado; público específico não detalhado.",
        ["Não há descrição, metas, prazo, orçamento ou governança do programa."])
    add("Emprego e renda", "Agricultura", 3, 4, "• Incentivo à agricultura familiar", "agronegócio;",
        "Propõe incentivar agricultura familiar e agronegócio.", "Incentivar os dois segmentos citados.", "Agricultura familiar e agronegócio.",
        ["O trecho possui caráter abrangente e não informa instrumentos, prioridade, metas, prazo ou recursos."])
    add("Emprego e renda", "Inovação e empreendedorismo", 2, 4, "• Estímulo à inovação tecnológica", "empreendedorismo;",
        "Propõe estimular inovação tecnológica e apoiar empreendedorismo.", "Estimular inovação e apoiar empreendedorismo.", "Empreendedores; público específico não detalhado.",
        ["Não há programa, modalidade de apoio, metas, prazo ou orçamento."])
    add("Emprego e renda", "Ambiente de negócios", 3, 4, "• Desburocratização dos serviços públicos", "investimentos.",
        "Propõe desburocratizar serviços públicos para atrair investimentos.", "Simplificar serviços com a finalidade declarada no trecho.", "Investidores e usuários dos serviços; público específico não detalhado.",
        ["Não há processos-alvo, medidas, metas, prazo ou estimativa de investimento."])

    # Assistência social e combate à fome
    add("Assistência social e combate à fome", "Apoio a famílias de pessoas com TEA", 3, 3, "• Criação de programas de apoio", "(TEA);",
        "Propõe criar programas de apoio às famílias de pessoas com TEA.", "Criar os programas de apoio indicados.", "Famílias de pessoas com Transtorno do Espectro Autista.",
        ["Não há conteúdo dos programas, cobertura, benefícios, prazo ou orçamento."])
    add("Assistência social e combate à fome", "Inclusão social", 1, 3, "• Ampliação das políticas públicas de inclusão social.", "social.",
        "Menciona ampliação de políticas públicas de inclusão social.", "Ampliar políticas de inclusão social.", "Não especificado no trecho.",
        ["Menção genérica sem público, política, ação operacional, meta, prazo ou recursos."])

    counts = Counter(); records = []
    for item in items:
        theme = item.pop("theme"); counts[theme] += 1
        records.append({"evidence_id": f"jeremias-{slug(theme)}-{counts[theme]:03d}", "candidate_id": "jeremias",
            "theme": theme, "subtheme": item.pop("subtheme"), "evidence_level": item.pop("evidence_level"),
            "neutral_summary": item.pop("neutral_summary"), "original_excerpt": item.pop("original_excerpt"),
            "page": f"p. {item.pop('page')}", "source_file": source["source_file"], "source_sha256": source["source_sha256"],
            "target_population": item.pop("target_population"), "proposed_action": item.pop("proposed_action"),
            "limitations": item.pop("limitations"), "prompt_version": PROMPT_VERSION, "model": "unavailable",
            "generated_at": generated_at, "review_status": "pending", "reviewed_at": None, "reviewer": None,
            "review_notes": "Aguarda revisão humana obrigatória."})
    absent = [theme for theme in allowed if not counts[theme]]
    output = {"records": records, "absence_report": [{"theme": theme, "pages_searched": list(range(1, 8)),
        "reason": "Nenhuma evidência localizada no texto extraído."} for theme in absent]}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True); OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    audit = {"candidate_id": "jeremias", "source": SOURCE.relative_to(ROOT).as_posix(), "source_file": source["source_file"],
        "source_sha256": source["source_sha256"], "prompt": PROMPT.relative_to(ROOT).as_posix(), "prompt_version": PROMPT_VERSION,
        "prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(), "model": "unavailable", "generated_at": generated_at,
        "page_count": source["page_count"], "evidence_count": len(records), "evidence_by_theme": dict(counts),
        "themes_analyzed": allowed, "themes_without_evidence": absent, "review_status": "pending",
        "limitations": ["Identificador real do modelo não disponível; registrado como 'unavailable'.",
                        "Trechos preservam literalmente o texto extraído.", *source.get("warnings", [])]}
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = "\n".join(f"- {theme}: {counts[theme]}" for theme in allowed)
    absent_lines = "Nenhum." if not absent else "\n".join(f"- {theme}" for theme in absent)
    REPORT.write_text(f"""# Evidências pendentes — Professor Jeremias

Fonte exclusiva: `data/generated/extracted-text/jeremias.json`  
SHA-256: `{source['source_sha256']}`  
Páginas analisadas: 1–7  
Prompt: `ai_pipeline/prompts/01_extract_candidate_evidence.md` (`{PROMPT_VERSION}`)

## Evidências por tema

{lines}

Total: {len(records)}.

## Temas sem evidência

{absent_lines}

Ausência não representa posição contrária.

## Validação e limitações

Validação estrutural prevista com o schema, `validate_evidence.py` e `validate_audit()`. Todos os registros permanecem `pending`. O identificador real do modelo não estava disponível. A fonte registra avisos estruturais do parser de PDF; os trechos localizados foram copiados literalmente. Propostas genéricas receberam nível conservador, e ausências de público, meta, prazo, recursos ou execução foram explicitadas.

## Revisão humana

Conferir trecho e página, tema, nível, separação ou consolidação de ações, neutralidade e limitações. Aprovar somente após confirmação integral; rejeitar se a fonte não sustentar o registro; solicitar correção para problemas sanáveis. Preencher revisor e data apenas após decisão humana.
""", encoding="utf-8")
    print(f"Jeremias: {len(records)} registros; ausentes: {absent}.")


if __name__ == "__main__": main()
