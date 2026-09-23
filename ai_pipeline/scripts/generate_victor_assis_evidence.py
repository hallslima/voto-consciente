from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"data/generated/extracted-text/victor_assis.json"; QUESTIONS=ROOT/"data/questions.json"; PROMPT=ROOT/"ai_pipeline/prompts/01_extract_candidate_evidence.md"
OUTPUT=ROOT/"data/generated/evidence/victor_assis.generated.json"; AUDIT=ROOT/"data/generated/evidence/victor_assis.generation-audit.json"; REPORT=ROOT/"docs/pilot-evidence-victor-assis.md"
VERSION="extract-evidence-v1.0.0"
def slug(v): return re.sub(r"[^a-z0-9]+","-",v.lower().translate(str.maketrans("áàâãéêíóôõúç","aaaaeeiooouc"))).strip("-")

def main():
    source=json.loads(SOURCE.read_text(encoding="utf-8")); pages={p["page_number"]:p["text"] for p in source["pages"]}; allowed=[q["theme"] for q in json.loads(QUESTIONS.read_text(encoding="utf-8"))]
    at=datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"); items=[]
    national="A fonte apresenta programa nacional e não especifica competência, adaptação ou execução pelo governo estadual."
    def add(theme,sub,level,page,start,end,summary,action,target,limits):
        text=pages[page]; a=text.find(start); b=text.find(end,a)
        if a<0 or b<0: raise ValueError(f"Trecho não localizado p. {page}: {start!r} / {end!r}")
        items.append(dict(theme=theme,subtheme=sub,evidence_level=level,page=page,original_excerpt=text[a:b+len(end)],neutral_summary=summary,proposed_action=action,target_population=target,limitations=[national,*limits]))

    # Saúde pública
    add("Saúde pública","Financiamento público",2,5,"• Mais verbas para a saúde pública.","vida do povo","Propõe ampliar verbas e não limitar gastos destinados à saúde pública.","Ampliar recursos para saúde pública.","População usuária da saúde pública.",["Não há valor, fonte, regra fiscal, prazo ou prioridade de aplicação."])
    add("Saúde pública","Rede de atendimento",3,5,"• Plano de emergência para construção","todo o País","Propõe plano emergencial para construir hospitais e postos de saúde em todo o país.","Criar e executar o plano de construção indicado.","População de todo o país.",["Não há quantidade, localização, prazo, orçamento ou modelo de gestão."])
    add("Saúde pública","Médicos e formação",3,5,"• Volta do programa Mais Médicos","profissionais","Propõe retomar Mais Médicos, validar diplomas e abrir cursos públicos de saúde para suprir profissionais.","Executar a estratégia de provimento e formação descrita.","Médicos residentes, estudantes e população afetada pela falta de profissionais.",["Trecho reúne ações da mesma estratégia, sem quantidade, critérios, vagas, prazo ou recursos."])
    add("Saúde pública","Remuneração profissional",3,5,"• Piso salarial de R$8 mil","saúde.","Propõe piso salarial de R$ 8 mil para profissionais da saúde.","Instituir o piso informado.","Profissionais da saúde.",["Não há referência temporal do valor, abrangência, fonte, mecanismo legal ou prazo."])

    # Educação
    add("Educação","Gestão democrática",3,5,"• Abaixo a ditadura nas escolas","postos de gestão","Propõe eleição direta dos postos de gestão escolar.","Realizar eleições diretas para os postos indicados.","Comunidade escolar; eleitores não detalhados neste trecho.",["Não há regras, abrangência, mandato ou prazo."])
    add("Educação","Financiamento público",2,5,"• Mais verbas para a educação","ensino público","Propõe mais recursos e destinação de verba pública somente ao ensino público.","Ampliar e restringir a destinação dos recursos conforme o trecho.","Ensino público.",["Não há valor, fonte, prazo ou critérios de distribuição."])
    add("Educação","Acesso ao ensino superior",2,5,"• Fim dos vestibulares.","universidades","Propõe encerrar vestibulares e adotar livre ingresso nas universidades.","Alterar o acesso universitário conforme o trecho.","Candidatos ao ensino superior.",["Não há transição, critérios de vagas, capacidade, prazo ou recursos."])
    add("Educação","Remuneração docente",3,5,"• Piso salarial nacional dos professores","R$8,5 mil","Propõe piso salarial nacional docente de pelo menos R$ 8,5 mil.","Instituir o piso indicado.","Professores.",["Não há referência temporal do valor, mecanismo legal, fonte ou prazo."])
    add("Educação","Controle comunitário",3,5,"• Escolas e Universidades sob o controle","Universidades","Propõe controle da comunidade escolar, eleição de direções e governo tripartite universitário.","Implantar os mecanismos de gestão descritos.","Estudantes, professores e funcionários.",["Não há regras eleitorais, transição, abrangência ou prazo."])
    add("Educação","Jornada docente",3,5,"• Jornada de trabalho dos professores","semanais","Propõe jornada docente máxima de 30 horas semanais.","Limitar a jornada conforme o trecho.","Professores.",["Não há composição da jornada, remuneração, abrangência ou prazo."])
    add("Educação","Gestão pública do ensino",2,5,"• Estatização do ensino pago","ensino pago","Propõe estatizar o ensino pago.","Estatizar o segmento indicado.","Instituições e usuários do ensino pago.",["Não há escopo, transição, indenização, modelo administrativo, prazo ou recursos."])

    # Segurança pública
    add("Segurança pública","Organização policial",2,5,"• Dissolução da polícia militar","aparato repressivo","Propõe dissolver a polícia militar e o aparato repressivo.","Dissolver as instituições mencionadas.","Não especificado no trecho.",["Não há instituição substituta, transição, salvaguardas, prazo ou forma de execução."])
    add("Segurança pública","Autodefesa",3,5,"• Direito de autodefesa","comunidades de índios","Propõe direito de autodefesa e formação de comitês para trabalhadores urbanos, rurais e comunidades indígenas.","Formar os comitês e reconhecer o direito descrito.","Trabalhadores da cidade e campo e comunidades indígenas.",["Não há estrutura, limites, supervisão, armamento, prazo ou implementação."])

    # Mobilidade e transporte
    add("Mobilidade e transporte","Passe livre",3,2,"• Passe livre nos transportes","economia informal.","Propõe passe livre para desempregados e trabalhadores da economia informal.","Conceder passe livre ao público indicado.","Desempregados e trabalhadores da economia informal.",["Não há modais, abrangência territorial, fonte de custeio, prazo ou operação."])

    # Emprego e renda
    add("Emprego e renda","Recomposição salarial",3,2,"• Reposição integral de 100%","todos os salários","Propõe reposição integral das perdas e aumento emergencial de 50% dos salários.","Reajustar salários conforme os percentuais indicados.","Trabalhadores assalariados.",["Não há base de cálculo, data de referência, mecanismo legal, fonte ou prazo."])
    add("Emprego e renda","Proteção contra inflação",3,2,"• Escala móvel dos salários","subir 3%","Propõe aumento salarial automático quando o custo de vida subir 3%.","Instituir escala móvel conforme o gatilho indicado.","Trabalhadores assalariados.",["Não há índice de preços, periodicidade, mecanismo legal ou implementação."])
    add("Emprego e renda","Salário mínimo",3,2,"• Salário mínimo vital","organizações operárias","Propõe salário mínimo suficiente às necessidades familiares, com referência de R$ 7.500 e deliberação por organizações operárias.","Instituir salário mínimo conforme referência e processo descritos.","Trabalhadores e suas famílias.",["O valor é apresentado como referência contemporânea sem data-base explícita; não há mecanismo legal ou prazo."])
    add("Emprego e renda","Redução da jornada",3,2,"• Redução da jornada de trabalho","todos trabalhem","Propõe jornada máxima de 35 horas semanais sem redução salarial como estratégia de emprego.","Reduzir a jornada aos limites indicados.","Trabalhadores e desempregados.",["Não há setores, transição, mecanismo legal, meta de empregos ou prazo."])
    add("Emprego e renda","Proteção contra demissões",3,2,"• Proibição das demissões","ameacem fechar","Propõe proibir demissões e estabelecer ocupação e controle de empresas que demitam ou ameacem fechar.","Aplicar as medidas trabalhistas descritas.","Trabalhadores de empresas que demitam ou ameacem encerrar atividades.",["O trecho tem caráter transversal e não define processo, autoridade, transição, prazo ou limites."])
    add("Emprego e renda","Direitos trabalhistas",3,3,"• Cancelamento da \"reforma\" trabalhista","proteção dos\ntrabalhadores","Propõe cancelar a reforma trabalhista e ampliar legislação protetiva.","Restabelecer e ampliar a proteção trabalhista descrita.","Trabalhadores.",["Não identifica dispositivos, competência estadual, transição ou prazo."])
    add("Emprego e renda","Serviço público",3,4,"• Contra as terceirizações","quadro de servidores.","Propõe estabilidade e isonomia a servidores precários e concursos periódicos para recompor quadros.","Regularizar vínculos e realizar concursos conforme o trecho.","Servidores contratados precariamente e candidatos ao serviço público.",["Não há vagas, carreiras, órgãos, cronograma ou orçamento."])

    # Assistência social e combate à fome
    add("Assistência social e combate à fome","Transferência de renda",3,2,"• Auxílio emergencial de verdade","caos atual","Propõe auxílio emergencial e Bolsa Família de pelo menos um salário mínimo durante a situação descrita.","Pagar os benefícios no valor e período indicados.","Beneficiários do auxílio emergencial e Bolsa Família; critérios não detalhados.",["Não define 'caos atual', critérios, fonte, competência estadual ou operacionalização."])
    add("Assistência social e combate à fome","Proteção a desempregados",3,2,"• Salário-desemprego igual","economia informal.","Propõe salário-desemprego, proteção contra despejos e cortes e passe livre a desempregados.","Aplicar o conjunto de proteções descritas.","Trabalhadores demitidos, desempregados e trabalhadores da economia informal.",["Trecho transversal reúne renda, moradia, serviços e transporte; não há critérios, custeio, prazo ou implementação."])

    counts=Counter(); records=[]
    for x in items:
        theme=x.pop("theme"); counts[theme]+=1
        records.append({"evidence_id":f"victor_assis-{slug(theme)}-{counts[theme]:03d}","candidate_id":"victor_assis","theme":theme,"subtheme":x.pop("subtheme"),"evidence_level":x.pop("evidence_level"),"neutral_summary":x.pop("neutral_summary"),"original_excerpt":x.pop("original_excerpt"),"page":f"p. {x.pop('page')}","source_file":source["source_file"],"source_sha256":source["source_sha256"],"target_population":x.pop("target_population"),"proposed_action":x.pop("proposed_action"),"limitations":x.pop("limitations"),"prompt_version":VERSION,"model":"unavailable","generated_at":at,"review_status":"pending","reviewed_at":None,"reviewer":None,"review_notes":"Aguarda revisão humana obrigatória."})
    absent=[t for t in allowed if not counts[t]]; output={"records":records,"absence_report":[{"theme":t,"pages_searched":list(range(1,8)),"reason":"Nenhuma evidência localizada no texto extraído."} for t in absent]}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    audit={"candidate_id":"victor_assis","source":SOURCE.relative_to(ROOT).as_posix(),"source_file":source["source_file"],"source_sha256":source["source_sha256"],"prompt":PROMPT.relative_to(ROOT).as_posix(),"prompt_version":VERSION,"prompt_sha256":hashlib.sha256(PROMPT.read_bytes()).hexdigest(),"model":"unavailable","generated_at":at,"page_count":source["page_count"],"evidence_count":len(records),"evidence_by_theme":dict(counts),"themes_analyzed":allowed,"themes_without_evidence":absent,"review_status":"pending","limitations":["Identificador real do modelo não disponível; registrado como 'unavailable'.","A fonte apresenta programa nacional e não detalha adaptação ou competência do governo estadual.","Trechos foram preservados literalmente e exigem revisão humana."]}
    AUDIT.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines="\n".join(f"- {t}: {counts[t]}" for t in allowed); absent_lines="Nenhum." if not absent else "\n".join(f"- {t}" for t in absent)
    REPORT.write_text(f"""# Evidências pendentes — Victor Assis

Fonte exclusiva: `data/generated/extracted-text/victor_assis.json`  
SHA-256: `{source['source_sha256']}`  
Páginas analisadas: 1–7  
Prompt: `ai_pipeline/prompts/01_extract_candidate_evidence.md` (`{VERSION}`)

## Evidências por tema

{lines}

Total: {len(records)}.

## Temas sem evidência

{absent_lines}

Ausência não representa posição contrária.

## Validação e limitações

Todos os registros permanecem `pending`. O identificador real do modelo não estava disponível. A fonte é apresentada como programa nacional e não detalha adaptação ou competência estadual; isso foi registrado sem inferência. Ações independentes foram separadas, estratégias integradas mantidas juntas e repetições não elevaram níveis.

## Revisão humana

Conferir trecho, página, competência, tema, nível, separação das ações, resumo e limitações. Aprovar somente após confirmação; rejeitar se a fonte não sustentar o registro; solicitar correção para problemas sanáveis. Preencher revisor e data apenas após decisão humana.
""",encoding="utf-8")
    print(f"Victor Assis: {len(records)} registros; ausentes: {absent}.")

if __name__=="__main__": main()
