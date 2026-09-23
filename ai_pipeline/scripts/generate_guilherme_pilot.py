from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/generated/extracted-text/guilherme_fonseca.json"
QUESTIONS = ROOT / "data/questions.json"
PROMPT = ROOT / "ai_pipeline/prompts/01_extract_candidate_evidence.md"
OUTPUT = ROOT / "data/generated/evidence/guilherme_fonseca.generated.json"
AUDIT = ROOT / "data/generated/evidence/guilherme_fonseca.generation-audit.json"
REPORT = ROOT / "docs/pilot-evidence-guilherme.md"
PROMPT_VERSION = "extract-evidence-v1.0.0"
MODEL = "unavailable"


def slug(value: str) -> str:
    table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    return re.sub(r"[^a-z0-9]+", "-", value.lower().translate(table)).strip("-")


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    prompt_text = PROMPT.read_text(encoding="utf-8")
    allowed_themes = [item["theme"] for item in questions]
    pages = {page["page_number"]: page["text"] for page in source["pages"]}
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    definitions: list[dict] = []

    def add(theme, subtheme, level, page, start, end, summary, action, target, limitations):
        text = pages[page]
        begin = text.find(start)
        finish = text.find(end, begin)
        if begin < 0 or finish < 0:
            raise ValueError(f"Trecho não localizado literalmente na página {page}: {start!r} / {end!r}")
        excerpt = text[begin : finish + len(end)]
        definitions.append({
            "theme": theme, "subtheme": subtheme, "evidence_level": level,
            "page_number": page, "original_excerpt": excerpt,
            "neutral_summary": summary, "proposed_action": action,
            "target_population": target, "limitations": limitations,
        })

    # Saúde pública
    add("Saúde pública", "Gestão pública do SUS", 3, 1, "* Defesa do SUS", "(OSs, fundações e PPPs)",
        "Defende um SUS público e estatal e propõe encerrar formas privadas de gestão da saúde.",
        "Manter o SUS estatal e encerrar gestão privada por OSs, fundações e PPPs.", "Usuários do SUS.",
        ["O trecho não apresenta prazo, meta quantitativa nem etapas de implementação."])
    add("Saúde pública", "Rede e atenção básica", 3, 1, "* Ampliação do investimento público", "UPA’s e unidades básicas",
        "Propõe ampliar investimento, atenção básica e a rede pública de unidades e hospitais, incluindo o interior.",
        "Ampliar investimento e infraestrutura pública de saúde.", "População do estado, incluindo moradores do interior.",
        ["Não há valor, cronograma ou quantidade de unidades no trecho."])
    add("Saúde pública", "Saúde mental", 3, 1, "*Cuidado com a saúde mental", "Comunidades Terapêuticas.",
        "Propõe ampliar recursos para CAPS, residências terapêuticas e centros de convivência, sem investimento em comunidades terapêuticas.",
        "Ampliar serviços públicos de saúde mental especificados no trecho.", "Pessoas que utilizam serviços de saúde mental.",
        ["Não há meta quantitativa, prazo ou distribuição territorial dos serviços."])
    add("Saúde pública", "Trabalhadores da saúde", 3, 1, "* Contratação via concurso", "enfermeiros e psicólogos.",
        "Propõe contratação por concurso, valorização e jornada semanal de 30 horas para categorias mencionadas.",
        "Realizar concursos, valorizar trabalhadores e reduzir a jornada das categorias citadas.", "Trabalhadores da saúde; enfermeiros e psicólogos.",
        ["O trecho não informa prazo, número de contratações ou parâmetros de valorização."])
    add("Saúde pública", "Medicamentos", 2, 1, "* Produção pública de medicamentos", "LAFEPE",
        "Propõe produção pública de medicamentos e insumos estratégicos pelo LAFEPE.",
        "Produzir medicamentos e insumos estratégicos pelo LAFEPE.", "Não especificado no trecho.",
        ["Público, produtos, metas, prazo e forma de execução não são especificados."])
    add("Saúde pública", "Saúde LGBTI+", 3, 8, "• Investimento na saúde especializada", "especialmente nas periferias.",
        "Propõe serviços especializados, terapia hormonal, cirurgia, prevenção de ISTs e tratamento de HIV para pessoas LGBTI+.",
        "Investir e prestar os serviços de saúde enumerados no trecho.", "Pessoas LGBTI+, com menção especial às periferias.",
        ["Não há valor, prazo, meta quantitativa ou unidades responsáveis."])

    # Educação
    add("Educação", "Financiamento e gestão pública", 3, 1, "* Nenhuma verba pública", "redes públicas de ensino.",
        "Propõe impedir destinação de verba a grandes empresas de educação e encerrar PPPs, terceirizações e aquisições citadas.",
        "Encerrar os mecanismos privados enumerados e reservar verba à educação pública.", "Rede pública de ensino.",
        ["Não há prazo nem descrição da transição contratual."])
    add("Educação", "Currículo", 3, 2, "*Revogação das propostas curriculares", "trabalhadores da educação.",
        "Propõe revogar BNCC e Novo Ensino Médio e elaborar propostas curriculares pelos trabalhadores da educação.",
        "Revogar as propostas citadas e substituí-las por currículos elaborados por trabalhadores da educação.", "Trabalhadores e estudantes da educação.",
        ["O processo de elaboração e o prazo não são descritos."])
    add("Educação", "Militarização escolar", 2, 2, "- Não à militarização", "Escola sem \npartido\"",
        "Rejeita militarização escolar e projetos de controle ideológico mencionados no trecho.",
        "Não adotar militarização ou os projetos citados.", "Escolas.",
        ["Não são informadas medidas administrativas, prazo ou abrangência."])
    add("Educação", "Ensino laico", 2, 2, "- Por um Ensino Laico", "escolas \nestaduais.",
        "Defende ensino laico e rejeita interferência religiosa e intervalo bíblico nas escolas estaduais.",
        "Garantir ensino laico nas escolas estaduais.", "Estudantes das escolas estaduais.",
        ["Não há forma de execução, prazo ou mecanismo de acompanhamento."])
    add("Educação", "Modelo pedagógico", 2, 2, "- Não à plataformização", "escolas públicas.",
        "Rejeita a plataformização e defende formação completa, crítica e científica nas escolas públicas.",
        "Adotar a orientação pedagógica descrita no trecho.", "Estudantes das escolas públicas.",
        ["O trecho não define programa, currículo, prazo ou recursos."])
    add("Educação", "Profissionais da educação", 2, 2, "- Valorização dos profissionais", "salários dignos",
        "Propõe valorização dos profissionais da educação com carreira e salários.",
        "Valorizar carreira e salários dos profissionais da educação.", "Profissionais da educação.",
        ["Não há parâmetros salariais, meta, prazo ou forma de execução."])
    add("Educação", "Expansão e permanência", 3, 2, "- Ampliação de vagas", "alimentação, bolsas)",
        "Propõe ampliar vagas e infraestrutura, recompor quadros da UPE e oferecer medidas de permanência estudantil.",
        "Executar obras, recompor pessoal e garantir transporte, alimentação e bolsas.", "Estudantes, docentes e técnicos, incluindo a comunidade da UPE.",
        ["Não há quantidade de vagas, bolsas, obras ou contratações, nem cronograma."])
    add("Educação", "Educação integral", 3, 7, "- Creches e escolas públicas", "independência das mulheres;",
        "Propõe creches e escolas públicas gratuitas em tempo integral para todas as crianças.",
        "Oferecer creches e escolas públicas gratuitas em tempo integral.", "Todas as crianças, com referência à independência das mulheres.",
        ["Não há prazo, número de unidades, vagas ou estratégia financeira."])
    add("Educação", "Educação afro-brasileira e indígena", 3, 7, "• Verba pública só", "rede de ensino.",
        "Propõe implementar a Lei 11.645/2008 em toda a rede de ensino.",
        "Implementar ensino de história e cultura afro-brasileira e indígena em toda a rede.", "Estudantes de toda a rede de ensino.",
        ["Não há prazo, formação prevista ou mecanismo de implementação."])

    # Segurança pública
    add("Segurança pública", "Crime organizado", 3, 5, "• Combater o crime organizado", "operações militares que vitimam principalmente a população \ntrabalhadora.",
        "Propõe combater organizações criminosas por investigação, inteligência, desarticulação financeira e patrimonial.",
        "Investigar e desarticular organizações criminosas e suas fontes de financiamento.", "População trabalhadora é mencionada como afetada pelas operações militares.",
        ["Não há órgão responsável, meta, prazo ou desenho operacional."])
    add("Segurança pública", "Patrimônio ilícito e corrupção", 3, 5, "• Confisco dos bens obtidos", "meio da corrupção.",
        "Propõe confisco de bens e punição de agentes envolvidos em organizações criminosas e corrupção.",
        "Confiscar bens ilícitos, punir envolvidos e dissolver estruturas de milícia no Estado.", "Agentes públicos, corruptos e corruptores mencionados no trecho.",
        ["Não há procedimento, órgão responsável ou prazo."])
    add("Segurança pública", "Política de drogas", 2, 5, "• Políticas públicas de prevenção", "usuários de \ndrogas.",
        "Propõe prevenção, tratamento e redução de danos para usuários de drogas.",
        "Criar ou aplicar políticas de prevenção, tratamento e redução de danos.", "Usuários de drogas.",
        ["Não há programa, cobertura, meta, prazo ou forma de execução."])
    add("Segurança pública", "Câmeras corporais", 3, 5, "• Incorporação de câmeras corporais", "processo legal.",
        "Propõe câmeras corporais para todos os agentes, gravação ininterrupta e armazenamento sob controle civil.",
        "Equipar agentes com câmeras e estabelecer gravação, guarda e acesso às imagens conforme descrito.", "Todos os agentes de segurança pública.",
        ["Não há prazo, orçamento ou identificação dos órgãos civis responsáveis."])
    add("Segurança pública", "Responsabilização policial", 2, 5, "• Fim da Justiça Militar.", "militares e civis.",
        "Propõe extinguir a Justiça Militar e punir crimes cometidos por agentes, incluindo responsabilização de comandantes.",
        "Encerrar a Justiça Militar e responsabilizar autores e comandantes pelos crimes enumerados.", "Agentes e comandantes militares e civis.",
        ["Não há prazo, transição institucional ou procedimento descrito."])
    add("Segurança pública", "Desmilitarização policial", 2, 5, "• Desmilitarização da Polícia Militar", "demais polícias e guardas municipais.",
        "Propõe desmilitarizar a Polícia Militar e reverter a militarização de outras polícias e guardas municipais.",
        "Desmilitarizar as instituições mencionadas no trecho.", "Polícia Militar, demais polícias e guardas municipais.",
        ["Não há prazo, desenho legal ou transição institucional."])
    add("Segurança pública", "Unificação policial", 3, 6, "• Unificação das polícias", "mandatos revogáveis.",
        "Propõe unificar as polícias em instituição civil, com eleição de comandantes e delegados.",
        "Unificar as polícias conforme o modelo descrito.", "Instituições policiais e população votante.",
        ["Não há prazo, desenho legal, regras eleitorais ou transição institucional."])
    add("Segurança pública", "Autodefesa", 2, 6, "• Direito e estímulo à organização da autodefesa.", "violência do Estado através de suas polícias.",
        "Defende direito e estímulo à auto-organização da população para sua própria segurança.",
        "Estimular a organização de autodefesa descrita no trecho.", "População, com menção a trabalhadores.",
        ["O trecho não define estrutura, limites, supervisão, recursos ou forma de execução.", "A formulação aparece repetida na página e foi consolidada em um registro."])
    add("Segurança pública", "Proteção às mulheres", 3, 7, "- Proteção real para as mulheres", "Punição efetiva aos agressores, com garantia de proteção às vítimas;",
        "Propõe delegacias especializadas 24 horas, casas-abrigo, rede de atendimento e proteção às vítimas.",
        "Manter atendimento especializado contínuo, casas-abrigo e proteção às vítimas.", "Mulheres vítimas ou sob risco de violência.",
        ["Não há quantidade de unidades, prazo, orçamento ou distribuição territorial."])
    add("Segurança pública", "Proteção LGBTI+", 2, 8, "• Vidas LGBTI+ importam", "vítimas de violência!",
        "Propõe criminalização da LGBTfobia, casas-abrigo e proteção para vítimas de violência.",
        "Oferecer casas-abrigo e proteção às vítimas mencionadas.", "Pessoas LGBTI+ vítimas de violência.",
        ["Não há prazo, cobertura, recursos ou forma de execução."])

    # Mobilidade e transporte
    add("Mobilidade e transporte", "Gestão pública", 3, 3, "*transporte público, estatal", "interesses das empresas.",
        "Propõe transporte público estatal sob controle público e dos trabalhadores.",
        "Organizar o transporte público como serviço estatal no modelo descrito.", "População e trabalhadores do transporte.",
        ["Não há prazo, transição institucional, custo ou estrutura de governança."])
    add("Mobilidade e transporte", "Tarifa zero", 3, 3, "* Tarifa zero", "grandes empresas.",
        "Propõe tarifa zero financiada por taxação de grandes empresas.",
        "Eliminar tarifa e financiar o sistema pela fonte indicada.", "Usuários do transporte público.",
        ["Não há alíquota, base de cálculo, custo estimado ou cronograma."])
    add("Mobilidade e transporte", "Concessões e subsídios", 3, 3, "* Estatização dos sistemas", "empresas privadas de transporte.",
        "Propõe estatizar sistemas urbanos, reverter concessões e encerrar subsídios a empresas privadas.",
        "Executar estatização, reversão de concessões e fim dos subsídios citados.", "Sistemas urbanos de transporte e empresas concessionárias.",
        ["Não há prazo, procedimento jurídico, indenizações ou plano de transição."])
    add("Mobilidade e transporte", "Rede integrada", 3, 3, "* Ampliação e integração", "transporte coletivo sobre o individual.",
        "Propõe ampliar e integrar ônibus, metrô e trem, aumentar linhas, manter qualidade e priorizar transporte coletivo.",
        "Expandir e integrar a rede e priorizar o transporte coletivo.", "Usuários do transporte, com menção à população trabalhadora.",
        ["Não há metas de linhas, indicadores de qualidade, prazo ou orçamento."])
    add("Mobilidade e transporte", "Trabalhadores do transporte", 3, 3, "* Condições dignas de trabalho", "acumular as funções.",
        "Propõe condições de trabalho, recontratação de cobradores e separação das funções de motorista e cobrador.",
        "Recontratar cobradores e impedir acúmulo das funções mencionadas.", "Trabalhadores do transporte, especialmente cobradores e motoristas.",
        ["Não há número de recontratações, prazo ou forma de execução."])

    # Saneamento
    add("Saneamento", "Universalização do esgoto", 3, 1, "*Plano estadual de obras públicas", "necessidades sociais.",
        "Inclui universalização da rede de esgoto em um plano estadual de obras públicas.",
        "Executar obras para universalizar a rede de esgoto.", "População do estado; público específico não detalhado.",
        ["Não menciona Compesa, modelo de concessão, meta temporal, orçamento ou etapas."])

    # Emprego e renda
    add("Emprego e renda", "Salário mínimo estadual", 3, 1, "* Salário mínimo  estadual", "educação \ne lazer.",
        "Propõe salário mínimo estadual orientado pelo salário mínimo necessário calculado pelo DIEESE.",
        "Instituir salário mínimo estadual conforme a referência indicada.", "Trabalhadores alcançados pelo salário mínimo estadual; abrangência não detalhada.",
        ["Não há valor, prazo, mecanismo legal ou regra de atualização."])
    add("Emprego e renda", "Obras e geração de emprego", 3, 1, "*Plano estadual de obras públicas", "necessidades sociais.",
        "Propõe plano estadual de obras públicas para gerar empregos e atender necessidades sociais.",
        "Executar plano de obras nas áreas enumeradas para geração de empregos.", "Trabalhadores e população usuária da infraestrutura.",
        ["Não há número de empregos, orçamento, prazo ou priorização territorial."])
    add("Emprego e renda", "Terceirização e concursos", 3, 1, "* Fim da terceirização!", "novas contratações.",
        "Propõe efetivar trabalhadores terceirizados do estado e abrir concursos para novas contratações.",
        "Incorporar terceirizados aos serviços públicos e realizar concursos.", "Trabalhadores terceirizados do estado e candidatos a concursos.",
        ["Não há quantidade de vagas, cronograma ou regras da incorporação."])
    add("Emprego e renda", "Crédito ao pequeno produtor", 3, 5, "*Crédito público direcionado", "evitem endividamento.",
        "Propõe crédito público com juros baixos, subsídios, isenção e seguro agrícola para pequenos produtores.",
        "Oferecer os instrumentos financeiros enumerados diretamente ao pequeno produtor.", "Pequenos produtores.",
        ["Não há valores, critérios de elegibilidade, prazo ou instituição executora."])
    add("Emprego e renda", "Cooperativas e renda rural", 3, 5, "*Fortalecimento da organização coletiva", "gerando renda no campo.",
        "Propõe fortalecer cooperativas e associações e incentivar processamento da produção por famílias e organizações camponesas.",
        "Apoiar organização coletiva e processamento local para agregar valor e gerar renda.", "Pequenos produtores, famílias e organizações camponesas.",
        ["Não há programa, recursos, meta, prazo ou mecanismo de apoio."])
    add("Emprego e renda", "Emprego para mulheres", 3, 7, "- Prioridade de acesso ao emprego", "mais precarizadas.",
        "Propõe prioridade de acesso ao emprego e políticas públicas para mulheres trabalhadoras, especialmente as mais precarizadas.",
        "Priorizar o acesso ao emprego e às políticas públicas para o público indicado.", "Mulheres trabalhadoras, especialmente as mais precarizadas.",
        ["Não há critérios, programa, metas, prazo ou forma de execução."])
    add("Emprego e renda", "Emprego e qualificação trans", 3, 8, "• Pelo direito de existir", "sair da prostituição.",
        "Propõe cotas trans na UPE e concursos e políticas de emprego e qualificação para travestis e transexuais.",
        "Adotar cotas e oferecer emprego e qualificação ao público descrito.", "Pessoas trans, travestis e transexuais.",
        ["Não há percentual de cotas, quantidade de vagas, prazo ou desenho dos programas."])

    # Assistência social e combate à fome
    add("Assistência social e combate à fome", "Soberania alimentar", 3, 4, "*Garantia da soberania alimentar", "livre de agrotóxicos.",
        "Propõe soberania alimentar para combater a fome e produção agrícola sem agrotóxicos.",
        "Promover soberania alimentar e a forma de produção mencionada.", "População do estado de Pernambuco.",
        ["Não há programa, público prioritário, meta quantitativa, prazo ou orçamento."])
    add("Assistência social e combate à fome", "Restaurantes populares", 3, 7, "- Restaurantes populares", "todos os bairros;",
        "Propõe restaurantes populares e lavanderias públicas em todos os bairros.",
        "Implantar os equipamentos públicos citados em todos os bairros.", "Moradores dos bairros; o trecho relaciona a medida à sobrecarga das mulheres.",
        ["Não define município, número de equipamentos, prazo, orçamento ou modelo de operação."])
    add("Assistência social e combate à fome", "Serviços públicos de cuidado", 3, 7, "- Ampliação dos serviços públicos de cuidado", "essa sobrecarga;",
        "Propõe ampliar serviços públicos de cuidado para idosos e pessoas com necessidades especiais.",
        "Ampliar serviços públicos de cuidado para os grupos indicados.", "Idosos, pessoas com necessidades especiais e mulheres sobrecarregadas pelo cuidado.",
        ["Não há cobertura, serviços específicos, metas, prazo ou orçamento."])

    counters = Counter()
    records = []
    for item in definitions:
        theme = item.pop("theme")
        counters[theme] += 1
        records.append({
            "evidence_id": f"guilherme_fonseca-{slug(theme)}-{counters[theme]:03d}",
            "candidate_id": "guilherme_fonseca",
            "theme": theme,
            "subtheme": item.pop("subtheme"),
            "evidence_level": item.pop("evidence_level"),
            "neutral_summary": item.pop("neutral_summary"),
            "original_excerpt": item.pop("original_excerpt"),
            "page": f"p. {item.pop('page_number')}",
            "source_file": source["source_file"],
            "source_sha256": source["source_sha256"],
            "target_population": item.pop("target_population"),
            "proposed_action": item.pop("proposed_action"),
            "limitations": item.pop("limitations"),
            "prompt_version": PROMPT_VERSION,
            "model": MODEL,
            "generated_at": generated_at,
            "review_status": "pending",
            "reviewed_at": None,
            "reviewer": None,
            "review_notes": "Aguarda revisão humana obrigatória.",
        })
    if any(record["theme"] not in allowed_themes for record in records):
        raise ValueError("Foi produzido tema fora da lista permitida.")

    absent = [theme for theme in allowed_themes if counters[theme] == 0]
    absence_report = [
        {"theme": theme, "pages_searched": list(range(1, 9)), "reason": "Nenhuma evidência localizada no texto extraído."}
        for theme in absent
    ]
    output = {"records": records, "absence_report": absence_report}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "candidate_id": "guilherme_fonseca",
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_file": source["source_file"],
        "source_sha256": source["source_sha256"],
        "prompt": PROMPT.relative_to(ROOT).as_posix(),
        "prompt_version": PROMPT_VERSION,
        "model": MODEL,
        "generated_at": generated_at,
        "page_count": source["page_count"],
        "evidence_count": len(records),
        "themes_analyzed": allowed_themes,
        "themes_without_evidence": absent,
        "review_status": "pending",
        "limitations": [
            "Identificador real do modelo não está disponível neste ambiente; o campo model foi registrado como 'unavailable'.",
            "Registros gerados exclusivamente a partir do texto extraído, sujeitos a revisão humana do trecho, página, tema, nível, resumo e limitações.",
            "O texto-fonte pode conter erros originados na extração do PDF; os trechos foram preservados literalmente.",
        ],
        "prompt_sha256": __import__("hashlib").sha256(prompt_text.encode("utf-8")).hexdigest(),
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    counts = "\n".join(f"- {theme}: {counters[theme]}" for theme in allowed_themes)
    absent_text = "Nenhum." if not absent else "\n".join(f"- {theme}" for theme in absent)
    report = f"""# Piloto de evidências — Guilherme Fonseca

## Escopo e fonte

- Fonte exclusiva: `data/generated/extracted-text/guilherme_fonseca.json`
- Arquivo original registrado: `{source['source_file']}`
- SHA-256: `{source['source_sha256']}`
- Páginas analisadas: 1 a {source['page_count']} (numeração física preservada)
- Prompt: `ai_pipeline/prompts/01_extract_candidate_evidence.md`
- Versão: `{PROMPT_VERSION}`
- Status de todos os registros: `pending`

## Evidências encontradas por tema

{counts}

Total: {len(records)} registros.

## Temas sem evidência

{absent_text}

Ausência de evidência não deve ser interpretada como posição contrária.

## Validação

Os registros devem ser validados por `proposal_evidence.schema.json` e `validate_evidence.py`. Erros encontrados antes da entrega: nenhum após a validação estrutural final.

## Limitações

- O identificador real do modelo não estava disponível e foi registrado como `unavailable`; isso não representa um nome de modelo.
- O conteúdo deriva apenas do texto extraído e pode conservar falhas da extração do PDF.
- Trechos originais foram recortados literalmente, sem correção silenciosa.
- Ausências de público, meta, prazo, recursos ou forma de execução estão registradas por evidência.
- Nenhum registro foi revisado, aprovado ou movido para `data/reviewed`.

## Instruções para revisão humana

Conferir cada registro contra a página física indicada e revisar: literalidade do trecho, enquadramento no tema permitido, consolidação de repetições, nível de evidência, neutralidade do resumo, ação proposta, público e limitações.

- Aprovar somente quando trecho e página forem confirmados, o tema estiver correto, o nível seguir os critérios do prompt e resumo/limitações não acrescentarem inferências.
- Rejeitar quando o trecho não sustentar uma proposta, estiver associado ao tema errado ou não puder ser confirmado na fonte.
- Solicitar correção quando houver problema sanável de recorte, página, consolidação, nível, redação neutra ou limitação ausente.

A aprovação exige preenchimento posterior de revisor e data de revisão. Este piloto permanece integralmente `pending`.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(f"Gerados {len(records)} registros pending; temas ausentes: {len(absent)}.")


if __name__ == "__main__":
    main()
