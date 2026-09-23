from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/generated/extracted-text/camila.json"
QUESTIONS = ROOT / "data/questions.json"
PROMPT = ROOT / "ai_pipeline/prompts/01_extract_candidate_evidence.md"
OUTPUT = ROOT / "data/generated/evidence/camila.generated.json"
AUDIT = ROOT / "data/generated/evidence/camila.generation-audit.json"
REPORT = ROOT / "docs/pilot-evidence-camila.md"
VERSION = "extract-evidence-v1.0.0"

def slug(v): return re.sub(r"[^a-z0-9]+", "-", v.lower().translate(str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc"))).strip("-")
def match(text, phrase, pos=0):
    pattern = r"\s+".join(re.escape(token) for token in phrase.split())
    found = re.search(pattern, text[pos:])
    if not found: raise ValueError(f"Âncora não localizada: {phrase!r}")
    return pos + found.start(), pos + found.end()

def main():
    source=json.loads(SOURCE.read_text(encoding="utf-8")); pages={p["page_number"]:p["text"] for p in source["pages"]}
    allowed=[q["theme"] for q in json.loads(QUESTIONS.read_text(encoding="utf-8"))]
    generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"); items=[]
    def add(theme,sub,level,page,start,end,summary,action,target,limits):
        text=pages[page]; a,_=match(text,start); _,b=match(text,end,a)
        items.append(dict(theme=theme,subtheme=sub,evidence_level=level,page=page,original_excerpt=text[a:b],neutral_summary=summary,proposed_action=action,target_population=target,limitations=limits))

    # Saúde pública
    add("Saúde pública","Gestão pública",3,4,"Fortalecimento do SUS:","gerenciam a saúde.","Defende encerrar repasses públicos a organizações sociais privadas que gerenciam a saúde.","Encerrar os repasses indicados.","Usuários e trabalhadores do SUS.",["Não há prazo, transição contratual, valores ou modelo administrativo substituto."])
    add("Saúde pública","Rede no interior",3,4,"Infraestrutura no Interior:","até a capital.","Propõe construir e equipar hospitais regionais de especialidades no Agreste, incluindo terapias para crianças atípicas.","Direcionar receita estadual para a infraestrutura descrita.","Moradores do Agreste e crianças atípicas, com referência a pacientes que se deslocam à capital.",["Não há quantidade de hospitais, locais, prazo, orçamento ou modelo de gestão."])
    add("Saúde pública","Profissionais no interior",3,4,"Interiorização de Profissionais:","interior do estado.","Propõe contratar por concurso médicos, enfermeiros e equipes técnicas para atuação no interior.","Realizar concursos estatutários e fixar profissionais no interior.","Médicos, enfermeiros, equipes técnicas e população do interior.",["Não há vagas, remuneração, lotação ou prazo."])
    add("Saúde pública","Saúde LGBTI+",3,4,"Políticas públicas de apoio à saúde", "profissionais da saúde.","Propõe ampliar acesso a PrEP e PEP para travestis e transexuais e oferecer educação em direitos humanos a profissionais.","Ampliar os acessos e realizar a formação descrita.","Travestis, transexuais e profissionais da saúde.",["O texto extraído associa siglas de modo possivelmente impreciso; requer conferência humana no original.","Não há cobertura, prazo, meta ou recursos."])
    add("Saúde pública","Atenção hospitalar e básica",2,2,"Ampliar a atenção médica", "valorizar os profissionais.","Propõe ampliar atenção médica em hospitais e postos e valorizar profissionais.","Ampliar atendimento e valorizar profissionais.","Usuários de hospitais e postos de saúde e seus profissionais.",["Não há modelo de gestão, ação operacional, meta, prazo ou recursos."])
    add("Saúde pública","Acesso universal",2,7,"Garantia de saúde pública", "planos de saúde privados;", "Defende saúde pública gratuita para todos e fim da exploração por planos privados.","Garantir saúde pública gratuita e executar a mudança indicada para planos privados.","Toda a população.",["Trecho pertence ao programa nacional reproduzido no plano; não detalha competência estadual, transição, prazo ou execução."])

    # Educação
    add("Educação","Financiamento e condições escolares",3,2,"Garantia de 10% do PIB", "profissionais da educação valorizados;", "Propõe destinar 10% do PIB estadual à educação, com merenda e valorização profissional.","Destinar o percentual e executar as medidas educacionais descritas.","Estudantes e profissionais da educação estadual.",["Não define base de cálculo, cronograma, padrão da merenda ou parâmetros de valorização."])
    add("Educação","Creches integrais",3,1,"Cuidados com a infância:","crianças típicas e atípicas.","Propõe ampliar e recuperar creches, com vagas integrais e profissionais habilitados para crianças típicas e atípicas.","Executar a expansão e melhoria da rede de creches.","Crianças típicas e atípicas, da capital ao sertão.",["Não há quantidade de vagas ou unidades, prazo ou orçamento."])
    add("Educação","UPE e escolas",3,2,"Vamos investir na ampliação da UPE", "funcionários valorizados.","Propõe ampliar a UPE e reformar escolas com merenda e valorização de professores e funcionários.","Investir na ampliação e reforma descritas.","Comunidade da UPE, estudantes e trabalhadores escolares.",["O trecho possui caráter transversal e não informa campi, escolas, metas, prazo ou recursos."])
    add("Educação","Interiorização do ensino superior",3,5,"Educação Pública e Acessível:","pública no interior.","Propõe enfrentar o sucateamento escolar e expandir vagas universitárias públicas no interior.","Recuperar escolas e expandir vagas no interior.","Estudantes de escolas públicas e do ensino superior no interior.",["Não há quantidade de vagas, instituições, obras, prazo ou orçamento."])
    add("Educação","Acesso universal",3,6,"Educação pública e gratuita", "qualquer processo seletivo.","Defende educação pública gratuita em todos os níveis e livre acesso a universidade ou cursos técnicos.","Garantir gratuidade e alterar mecanismos de acesso conforme o trecho.","Toda a população.",["Trecho pertence ao programa nacional e não detalha competência estadual, transição, vagas, prazo ou recursos."])

    # Segurança pública
    add("Segurança pública","Atendimento à mulher",3,1,"Combate à violência de gênero:","aparato psicológico/jurídico.","Propõe funcionamento 24 horas das Delegacias da Mulher com reforço de viaturas, efetivo e atendimento psicológico e jurídico.","Expandir horário e estrutura das delegacias especializadas.","Mulheres que demandem atendimento especializado.",["O trecho informa situação atual, mas não define prazo, número de viaturas, efetivo ou orçamento."])
    add("Segurança pública","Polícia Militar",2,8,"Pelo fim da polícia militar;", "movimentos sociais;", "Defende o fim da polícia militar e da repressão a movimentos sociais.","Encerrar a polícia militar e a repressão mencionada.","Movimentos sociais; demais públicos não especificados.",["Trecho pertence ao programa nacional e não define instituição substituta, transição, competência, prazo ou execução."])

    # Mobilidade e transporte
    add("Mobilidade e transporte","Metrô público",3,1,"Fim e reversão das privatizações:","metrô do Recife", "Propõe suspender imediatamente a privatização do Metrô do Recife.","Suspender o processo de privatização.","Usuários e trabalhadores do Metrô do Recife; público não explicitado no trecho.",["O recorte integra um parágrafo transversal sobre diferentes empresas; não há plano de gestão, prazo posterior ou recursos."])
    add("Mobilidade e transporte","Participação orçamentária",3,2,"conselhos populares formados", "transporte e creches.","Propõe que conselhos populares deliberem sobre investimentos, incluindo transporte.","Dar aos conselhos citados deliberação sobre os investimentos.","Trabalhadores e movimentos populares mencionados.",["A ação é transversal a saneamento, transporte e creches; não há regra de composição, competência, prazo ou orçamento."])
    add("Mobilidade e transporte","Rodovias e pedágios",2,5,"Extinção do modelo de concessões", "pequenos agricultores e feirantes.","Propõe extinguir concessões rodoviárias e cobrança de pedágios.","Encerrar o modelo e a cobrança indicados.","Pequenos agricultores, feirantes e demais usuários das rodovias.",["Não há contratos, trechos, transição, prazo ou fonte de manutenção."])
    add("Mobilidade e transporte","Transporte coletivo estatal",2,6,"Estatização de todos os meios", "transporte coletivo.","Propõe estatizar todos os meios de transporte coletivo.","Estatizar os meios de transporte coletivo.","Usuários e trabalhadores do transporte coletivo; não especificado no trecho.",["Trecho pertence ao programa nacional e não detalha competência estadual, tarifa, transição, prazo ou recursos."])

    # Saneamento
    add("Saneamento","Controle público da Compesa",3,1,"Suspensão imediata do processo", "controle 100% público", "Propõe suspender a concessão ou venda da Compesa e restabelecer controle público.","Bloquear a concessão ou venda e manter controle público.","População atendida pela Compesa.",["O trecho é transversal a outras privatizações e não detalha gestão, transição, prazo ou recursos."])
    add("Saneamento","Universalização pública",3,4,"Universalização Pública do Saneamento:","adutoras para o interior.","Propõe investimento direto estadual para ampliar redes de distribuição e adutoras no interior.","Investir na expansão da infraestrutura descrita.","População do interior.",["Não há localidades, cobertura, meta temporal, valor ou cronograma."])
    add("Saneamento","Consórcios privados",2,3,"Fim dos consórcios privados regionalizados.","iniciativa privada.","Propõe extinguir consórcios intermunicipais desenhados para transferência privada dos serviços de água e saneamento.","Extinguir os consórcios descritos.","População atendida por serviços de água e saneamento.",["Não identifica consórcios, transição, prazo ou arranjo substituto."])
    add("Saneamento","Infraestrutura hídrica rural",3,4,"Infraestrutura de Convivência:","agricultura familiar", "Propõe programas estatais de cisternas, barreiros e irrigação para assentamentos e agricultura familiar.","Implementar os programas e infraestruturas indicados.","Assentamentos da reforma agrária e produtores da agricultura familiar.",["Trecho tem caráter transversal entre água, produção e saneamento; não há metas, prazo, localidades ou orçamento."])

    # Emprego e renda
    add("Emprego e renda","Jornada e salário mínimo",3,2,"Valorização do Trabalho:","poder de compra da população.","Propõe apoio ao fim da escala 6x1 e aumento de 100% do salário mínimo.","Apoiar as mudanças trabalhistas e salariais descritas.","Trabalhadores e população afetada pelo salário mínimo.",["Não detalha competência estadual, mecanismo, valor resultante, prazo ou implementação.","Proposta repetida em outras páginas e consolidada sem elevar o nível."])
    add("Emprego e renda","Frentes públicas de trabalho",3,3,"Infraestrutura Estatal:","próprias localidades.","Propõe frentes públicas regionalizadas para executar obras e gerar empregos locais.","Criar as frentes e executar obras estruturais.","Trabalhadores das localidades e regiões do estado.",["Não há quantidade de postos, obras, vínculos, prazo ou orçamento."])
    add("Emprego e renda","Direitos no trabalho",3,3,"Combate à Exploração no Trabalho:","fornecimento de EPIs.","Propõe fiscalização trabalhista no polo têxtil e comércio do Agreste, com defesa de direitos e EPIs.","Realizar fiscalizações rigorosas para garantir os direitos enumerados.","Trabalhadores de confecções e comércio do Agreste.",["Trecho também repete escala e salário, consolidados em outro registro; não há equipe, meta, prazo ou órgão executor."])
    add("Emprego e renda","Pequeno produtor e comércio",3,3,"Apoio Direto ao Pequeno Produtor:","pequenos comerciantes locais.","Propõe direcionar recursos e crédito à agricultura familiar e infraestrutura a feirantes e pequenos comerciantes.","Canalizar crédito e recursos e garantir a infraestrutura mencionada.","Agricultura familiar, feirantes e pequenos comerciantes locais.",["O trecho reúne apoio financeiro e infraestrutura; não há valores, critérios, prazo ou órgãos executores."])
    add("Emprego e renda","Emprego jovem",3,5,"Geração de Emprego Digno:","habitação popular", "Propõe fomentar empregos formais por investimentos estatais em habitação popular e saneamento.","Gerar postos formais por meio dos investimentos indicados.","Juventude do interior, conforme o título da seção.",["A frase continua com saneamento fora do recorte temático; não há postos, obras, prazo ou orçamento."])
    add("Emprego e renda","Garantia de trabalho",2,6,"Garantia de emprego e trabalho", "trabalho infantil;", "Defende trabalho para pessoas adultas capazes e proibição do trabalho infantil.","Garantir trabalho adulto e proibir exploração infantil.","Pessoas adultas capazes de trabalhar e crianças sujeitas à exploração.",["Trecho pertence ao programa nacional e não define instrumentos, competência estadual, prazo ou recursos."])

    # Assistência social e combate à fome
    add("Assistência social e combate à fome","Participação popular",3,2,"conselhos populares formados", "transporte e creches.","Propõe conselhos populares para deliberar sobre investimentos em serviços sociais e infraestrutura.","Instituir deliberação popular sobre os investimentos enumerados.","Trabalhadores e movimentos populares mencionados.",["A evidência é transversal e não especifica assistência social diretamente, regras dos conselhos, prazo ou orçamento."])
    add("Assistência social e combate à fome","Soberania alimentar",3,3,"A agricultura deve visar", "combatendo a fome", "Propõe orientar agricultura à soberania alimentar, abastecimento local e mercados públicos para combater a fome.","Estimular produção destinada ao abastecimento local e mercados públicos.","População em situação de fome, produtores e consumidores locais.",["O trecho tem caráter transversal com política agrícola; não há metas, público prioritário, prazo ou recursos."])

    counts=Counter(); records=[]
    for x in items:
        theme=x.pop("theme"); counts[theme]+=1
        records.append({"evidence_id":f"camila-{slug(theme)}-{counts[theme]:03d}","candidate_id":"camila","theme":theme,"subtheme":x.pop("subtheme"),"evidence_level":x.pop("evidence_level"),"neutral_summary":x.pop("neutral_summary"),"original_excerpt":x.pop("original_excerpt"),"page":f"p. {x.pop('page')}","source_file":source["source_file"],"source_sha256":source["source_sha256"],"target_population":x.pop("target_population"),"proposed_action":x.pop("proposed_action"),"limitations":x.pop("limitations"),"prompt_version":VERSION,"model":"unavailable","generated_at":generated_at,"review_status":"pending","reviewed_at":None,"reviewer":None,"review_notes":"Aguarda revisão humana obrigatória."})
    absent=[t for t in allowed if not counts[t]]; output={"records":records,"absence_report":[{"theme":t,"pages_searched":list(range(1,9)),"reason":"Nenhuma evidência localizada no texto extraído."} for t in absent]}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"candidate_id":"camila","source":SOURCE.relative_to(ROOT).as_posix(),"source_file":source["source_file"],"source_sha256":source["source_sha256"],"prompt":PROMPT.relative_to(ROOT).as_posix(),"prompt_version":VERSION,"prompt_sha256":hashlib.sha256(PROMPT.read_bytes()).hexdigest(),"model":"unavailable","generated_at":generated_at,"page_count":source["page_count"],"evidence_count":len(records),"evidence_by_theme":dict(counts),"themes_analyzed":allowed,"themes_without_evidence":absent,"review_status":"pending","limitations":["Identificador real do modelo não disponível; registrado como 'unavailable'.","Trechos preservam literalmente espaçamento e quebras do texto extraído.","Parte da fonte reproduz um programa nacional; a competência estadual não foi inferida."]}
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines="\n".join(f"- {t}: {counts[t]}" for t in allowed); absent_lines="Nenhum." if not absent else "\n".join(f"- {t}" for t in absent)
    REPORT.write_text(f"""# Evidências pendentes — Professora Camila

Fonte exclusiva: `data/generated/extracted-text/camila.json`  
SHA-256: `{source['source_sha256']}`  
Páginas analisadas: 1–8  
Prompt: `ai_pipeline/prompts/01_extract_candidate_evidence.md` (`{VERSION}`)

## Evidências por tema

{lines}

Total: {len(records)}.

## Temas sem evidência

{absent_lines}

## Validação e limitações

Todos os registros permanecem `pending`. O identificador real do modelo não estava disponível. A extração contém espaçamento e quebras incomuns, preservados nos trechos. Parte do documento reproduz programa nacional; nenhuma competência estadual foi inferida. Ações transversais foram sinalizadas e repetições consolidadas sem elevar nível.

## Revisão humana

Conferir fonte, página, literalidade, competência, tema, nível, consolidação e limitações. Aprovar somente após confirmação; rejeitar se o trecho não sustentar a evidência; solicitar correção para problemas sanáveis. Preencher revisor e data apenas após decisão humana.
""",encoding="utf-8")
    print(f"Camila: {len(records)} registros; ausentes: {absent}.")

if __name__=="__main__": main()
