import { StrictMode, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const NO_OPINION = 'NO_OPINION';
const WEIGHT_LABELS = { 1: 'Normal', 2: 'Importante', 3: 'Prioridade máxima' };

function initials(name) {
  return name.split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase();
}

function App() {
  const [data, setData] = useState(null);
  const [answers, setAnswers] = useState({});
  const [weights, setWeights] = useState({});
  const [results, setResults] = useState(null);
  const [selectedId, setSelectedId] = useState(null);
  const [openId, setOpenId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [view, setView] = useState('product');

  useEffect(() => {
    fetch(`${API_URL}/api/bootstrap`)
      .then((response) => {
        if (!response.ok) throw new Error('Não foi possível carregar a matriz.');
        return response.json();
      })
      .then((payload) => {
        setData(payload);
        const initialAnswers = Object.fromEntries(payload.questions.map((question) => [question.id, NO_OPINION]));
        const initialWeights = Object.fromEntries(payload.questions.map((question) => [question.id, 2]));
        setAnswers(initialAnswers);
        setWeights(initialWeights);
      })
      .catch((reason) => setError(reason.message))
      .finally(() => setLoading(false));
  }, []);

  const answeredCount = useMemo(
    () => Object.values(answers).filter((answer) => answer !== NO_OPINION).length,
    [answers],
  );

  function setAnswer(questionId, optionId) {
    setAnswers((current) => ({ ...current, [questionId]: optionId }));
  }

  async function calculate() {
    if (!answeredCount) {
      setError('Escolha pelo menos uma alternativa para calcular sua correspondência.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/api/results`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers, weights }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível calcular os resultados.');
      setResults(payload.results);
      setSelectedId(payload.results[0]?.candidate_id || null);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (reason) {
      setError(reason.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="loading-screen">Carregando a matriz de propostas...</div>;
  if (error && !data) return <div className="loading-screen error-screen">{error}</div>;

  const candidateById = Object.fromEntries(data.candidates.map((candidate) => [candidate.id, candidate]));

  return (
    <main>
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand-mark">VC</span><span>Voto <strong>Consciente</strong></span></a>
        <nav className="main-nav" aria-label="Navegação principal"><button type="button" className={view === 'presentation' ? 'nav-active' : ''} onClick={() => setView('presentation')}>Apresentação</button><a href="#como-funciona" onClick={() => setView('product')}>Como funciona</a><a href="#questionario" onClick={() => setView('product')}>Questionário</a><a href="#metodo" onClick={() => setView('product')}>Método</a></nav>
        <span className="edition">Pernambuco · 2026</span>
      </header>
      {view === 'presentation' ? <PresentationSlides data={data} onOpenDemo={() => { setView('product'); window.setTimeout(() => document.getElementById('questionario')?.scrollIntoView({ behavior: 'smooth' }), 0); }} /> : <><section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Eleições · Pernambuco 2026</p>
          <h1>Seu voto começa<br /><em>nas suas prioridades.</em></h1>
          <p className="hero-text">Responda aos temas que importam para você e veja como suas escolhas se aproximam das propostas documentadas nos planos de governo.</p>
          <div className="hero-actions"><a className="primary-button hero-button" href="#questionario">Começar questionário <span>↓</span></a><a className="quiet-link" href="#como-funciona">Entenda antes de começar →</a></div>
          <div className="trust-line"><span className="trust-dot" /> Sem cadastro <span className="dot-separator">·</span> Suas respostas ficam neste dispositivo <span className="dot-separator">·</span> Dados oficiais</div>
        </div>
        <div className="hero-demo" aria-label="Demonstração do questionário"><div className="demo-label">Como você pensa?</div><div className="demo-card"><span className="demo-index">01 / {data.questions.length}</span><h2>Qual tema deve receber mais atenção?</h2><p>Escolha uma alternativa que represente melhor a sua prioridade.</p><div className="demo-options"><span className="demo-option active"><i /> Saúde pública</span><span className="demo-option"><i /> Educação</span><span className="demo-option"><i /> Segurança</span></div><div className="demo-foot"><span>uma pergunta por vez</span><span>→</span></div></div></div>
      </section>

      <section className="how-it-works" id="como-funciona"><div className="how-intro"><p className="eyebrow">Uma leitura, não uma indicação</p><h2>Você responde.<br /><em>A gente organiza.</em></h2><p>O resultado não escolhe por você. Ele transforma suas prioridades em uma forma simples de comparar propostas e investigar as diferenças.</p></div><div className="steps"><div className="step"><span>01</span><h3>Você responde</h3><p>Indique suas preferências e o peso de cada tema para a sua decisão.</p></div><div className="step"><span>02</span><h3>A gente calcula</h3><p>Comparamos suas respostas com evidências classificadas nos planos.</p></div><div className="step"><span>03</span><h3>Você analisa</h3><p>Veja a proximidade, a cobertura e a fonte por candidatura.</p></div></div></section>

      {!results ? (
        <Questionnaire data={data} answers={answers} weights={weights} setAnswer={setAnswer} setWeights={setWeights} answeredCount={answeredCount} onCalculate={calculate} submitting={submitting} error={error} />
      ) : (
        <ResultsView results={results} candidates={candidateById} selectedId={selectedId} setSelectedId={setSelectedId} openId={openId} setOpenId={setOpenId} onRestart={() => setResults(null)} />
      )}</>}
      <footer><span>VOTO CONSCIENTE</span><span>A correspondência não avalia viabilidade, qualidade ou cumprimento das propostas.</span></footer>
    </main>
  );
}

function PresentationSlides({ data, onOpenDemo }) {
  return (
    <section className="slide-deck">
      <div className="deck-cover"><div><p className="eyebrow">MBA em Ciência de Dados e Inteligência Artificial · 15 minutos</p><h1>Voto Consciente<br /><em>Pernambuco</em></h1><p>Comparação auditável entre prioridades do eleitor e propostas dos planos de governo.</p><div className="cover-team"><span>Hallisson Lima</span><span>Rodrigo Monteiro</span><span>Lucas Kamel</span><span>Thamyres Costa</span><span>Ben-Hur Cavalcanti</span></div></div><div className="deck-brand"><span className="brand-mark">VC</span><b>Voto<br />Consciente</b><small>Pernambuco · 2026</small></div></div>
      <div className="deck-toolbar"><span>Roteiro · 16 minutos</span><a href="#slide-1">01 Capa</a><a href="#slide-2">02 Problema</a><a href="#slide-research">03 Necessidade</a><a href="#slide-3">04 Pesquisa</a><a href="#slide-4">05 Dados</a><a href="#slide-5">06 IA</a><a href="#slide-6">07 Perguntas</a><a href="#slide-7">08 Arquitetura</a><a href="#slide-8">09 ICT</a><a href="#slide-9">10 Exemplo</a><a href="#slide-10">11 Testes</a><a href="#slide-11">12 MVP</a><a href="#slide-12">13 Conclusão</a></div>
      <div className="slide-list">
        <PresentationSlide id="slide-1" number="01" time="30 segundos" title="Voto Consciente Pernambuco" label="Capa da apresentação"><p>Comparação auditável entre prioridades do eleitor e propostas dos planos de governo.</p><div className="cover-subline">MBA em Ciência de Dados e Inteligência Artificial · Pernambuco, 2026</div></PresentationSlide>
        <PresentationSlide id="slide-2" number="02" time="2 minutos" title="Por que é difícil comparar planos de governo?" label="Problema investigado"><p>Os documentos possuem estruturas e níveis de detalhamento diferentes, são extensos e não seguem uma organização temática única. Para comparar saúde, educação ou segurança, o eleitor precisa consultar vários arquivos e localizar as evidências.</p><div className="pdf-problem"><div className="pdf-stack"><span>PLANO.pdf</span><span>PROGRAMA.pdf</span><span>DIRETRIZES.pdf</span></div><div className="searching-voter"><b>eleitor</b><span>⌕</span><small>“onde está a proposta sobre saúde?”</small></div><div className="problem-topics"><i>Saúde</i><i>Educação</i><i>Segurança</i></div></div></PresentationSlide>
        <PresentationSlide id="slide-research" number="03" time="1,5 minuto" title="Evidências da necessidade do projeto" label="Pesquisa própria"><div className="research-metrics">{data.research_evidence.results.slice(0, 5).map((item) => <div className="research-metric" key={item.indicator}><strong>{item.percentage.toFixed(1).replace('.', ',')}%</strong><span>{item.indicator}</span><div><i style={{ width: `${item.percentage}%` }} /></div></div>)}</div><p className="research-sample"><b>{data.research_evidence.sample_size} participantes.</b> Pesquisa exploratória com amostra por conveniência, divulgada na rede de contatos do grupo. Os resultados descrevem somente o grupo consultado e não representam todo o eleitorado pernambucano.</p></PresentationSlide>
        <PresentationSlide id="slide-3" number="03" time="1 minuto" title="Pergunta de pesquisa e objetivo" label="Pergunta, objetivo e recorte"><div className="research-question"><small>Pergunta de pesquisa</small><strong>Como uma ferramenta baseada em dados públicos pode ajudar o eleitor a comparar suas prioridades com propostas verificáveis dos candidatos ao Governo de Pernambuco?</strong></div><div className="objective-grid"><div><b>Objetivo geral</b><p>Desenvolver e avaliar uma ferramenta que relacione as prioridades indicadas pelo eleitor com propostas documentadas nos planos de governo.</p></div><div><b>Recorte</b><p>Governo de Pernambuco · {data.candidates.length} candidaturas · {data.questions.length} temas · planos consultados no TSE · sem recomendação de voto.</p></div></div></PresentationSlide>
        <PresentationSlide id="slide-4" number="04" time="1 minuto" title="Base de dados do projeto" label="Dados utilizados"><p>A matriz reúne dados cadastrais, perguntas, posições classificadas e a localização da evidência nos documentos analisados.</p><div className="data-summary"><div className="data-count"><strong>{data.candidates.length}</strong><span>planos e candidaturas</span></div><div className="data-count"><strong>{data.questions.length}</strong><span>temas do MVP</span></div><div className="data-fields"><b>Campos da matriz</b><span>Candidato · tema · alternativa principal · compatibilidade · resumo · fonte · localização · nível de evidência</span></div></div><div className="topic-strip"><span>Saúde</span><span>Educação</span><span>Segurança pública</span><span>Mobilidade e transporte</span><span>Saneamento</span><span>Emprego e renda</span><span>Assistência social e combate à fome</span></div></PresentationSlide>
        <PresentationSlide id="slide-5" number="05" time="1,5 minuto" title="Inteligência Artificial na construção da base" label="Dados e inteligência artificial"><p>A Inteligência Artificial foi utilizada na etapa de construção da base, auxiliando na leitura, extração e organização das propostas. Durante o uso, o resultado é calculado por um algoritmo determinístico em Python.</p><div className="architecture-flow"><ArchNode icon="01" title="Planos oficiais" text="Cada plano analisado separadamente"/><span>→</span><ArchNode icon="02" title="Gemini" text="Extração assistida"/><span>→</span><ArchNode icon="03" title="Matriz temática" text="Propostas e evidências"/><span>→</span><ArchNode icon="04" title="Revisão humana" text="Aprovação da base"/></div><div className="ai-responsibility"><div><b>Participação da IA</b><span>Extração assistida · organização temática · identificação de diferenças · apoio à criação das perguntas</span></div><div><b>Responsabilidade humana</b><span>Conferência do trecho e página · validação da classificação · revisão de ambiguidades · aprovação da matriz final</span></div></div><div className="deterministic-note">A IA não recomenda candidatos, não participa do ranking e não calcula o resultado durante a execução.</div></PresentationSlide>
        <PresentationSlide id="slide-6" number="06" time="1 minuto" title="Das propostas ao questionário" label="Construção das perguntas"><div className="question-building"><ol><li>Identificação dos temas.</li><li>Agrupamento de propostas semelhantes.</li><li>Identificação das diferenças.</li><li>Transformação em alternativas.</li><li>Revisão da neutralidade.</li><li>Vinculação às evidências originais.</li></ol><div className="health-example"><small>Exemplo · Saúde</small><div><span>Administração direta</span><span>OSs com fiscalização</span><span>Parcerias privadas</span></div><b>Qual modelo de gestão deve receber prioridade nos hospitais públicos e nas unidades estaduais de saúde?</b></div></div><p className="general-mode"><b>Modo Geral · regra atual:</b> uma pergunta pode entrar quando existe proposta documentada em pelo menos uma candidatura. A ausência aparece na cobertura. As alternativas representam abordagens identificadas nos planos, não opiniões do grupo.</p></PresentationSlide>
        <PresentationSlide id="slide-7" number="07" time="1 minuto" title="Arquitetura do MVP" label="Arquitetura tecnológica"><div className="architecture-stack"><ArchNode icon="01" title="React" text="Interface e questionário"/><span>↓</span><ArchNode icon="02" title="FastAPI" text="Recebimento e validação"/><span>↓</span><ArchNode icon="03" title="Python" text="ICT, cobertura e ordenação"/><span>↓</span><ArchNode icon="04" title="JSON" text="Perguntas, candidatos e matriz"/></div><div className="technology-table"><div><b>Tecnologia</b><b>Responsabilidade</b></div><div><span>Vite · React</span><span>Desenvolvimento, build e interface</span></div><div><span>FastAPI · Pydantic</span><span>API e validação de respostas/pesos</span></div><div><span>Python · JSON</span><span>Motor, matriz e dados estruturados</span></div><div><span>CSS · SVG · Pytest</span><span>Visualizações e testes</span></div><div><span>Gemini</span><span>Apoio anterior à preparação dos dados</span></div></div><p className="architecture-note">O frontend não calcula o resultado: envia respostas e pesos para a API, e o motor Python devolve pontuações, cobertura e memória de cálculo.</p></PresentationSlide>
        <PresentationSlide id="slide-8" number="08" time="1,5 minuto" title="Índice de Correspondência Temática" label="Motor matemático"><div className="score-definition"><strong>P(k,q) = W(q) × S(k,q)</strong><p>W(q) é o peso atribuído pelo usuário. S(k,q) é a compatibilidade entre a resposta e a posição classificada.</p></div><div className="equation-grid"><div><small>ICT da candidatura</small><strong>ICT(k) = 100 × <b>Σ(W(q) × S(k,q))</b><br />/ ΣW(q)</strong><p>A soma inclui apenas perguntas respondidas e com evidência classificada.</p></div><div><small>ICP / cobertura do recorte respondido</small><strong>ICP(k) = <b>temas com evidência</b><br />/ temas respondidos × 100</strong><p>No código atual, este indicador é exposto como <b>coverage</b>.</p></div></div><div className="rule-strip"><span><b>1</b> direta</span><span><b>0,5</b> parcial</span><span><b>0</b> diferente</span><span><b>1 · 2 · 3</b> pesos</span></div><p className="calculation-rules">“Não tenho opinião” sai do cálculo de todas as candidaturas. Tema sem evidência fica fora do ICT daquela candidatura, não recebe nota zero e reduz a cobertura.</p></PresentationSlide>
        <PresentationSlide id="slide-9" number="09" time="1 minuto" title="Exemplo de cálculo auditável" label="Pontuação"><div className="simulation-table"><div className="sim-head"><span>Tema</span><span>Peso</span><span>Compatibilidade</span><span>Pontos</span></div><div><b>Saúde</b><strong>3</strong><strong>1,0</strong><strong>3,0</strong></div><div><b>Segurança</b><strong>2</strong><strong>0,0</strong><strong>0,0</strong></div><div><b>Transporte</b><strong>2</strong><strong>0,5</strong><strong>1,0</strong></div><div><b>Saneamento</b><span>1</span><em>Sem evidência</em><em>Não entra</em></div></div><div className="simulation-result"><span>Pontos obtidos = 4,0 · Pesos válidos = 7,0</span><strong>ICT = 57,1%</strong><small>Cobertura = 3 / 4 × 100 = 75%</small></div><p className="audit-caption">O ICT mostra a correspondência onde existe evidência. A cobertura mostra quanto do recorte respondido pôde ser comparado.</p></PresentationSlide>
        <PresentationSlide id="slide-10" number="10" time="1 minuto" title="Como verificamos o funcionamento" label="Validação e testes"><div className="tests-grid"><div><b>Testes automatizados</b><span>Não tenho opinião é ignorado</span><span>Correspondência total chega a 100%</span><span>Ausência reduz cobertura</span><span>Compatibilidades 0, 0,5 e 1</span><span>Resultados entre 0% e 100%</span><span>Ordenação por maior ICT</span></div><div><b>Regras validadas no código</b><span>Pesos aceitos: 1, 2 e 3</span><span>Perfis de respostas simulados</span><span>Matriz sem alternativas inválidas</span><span>API rejeita perguntas desconhecidas</span><span>API rejeita pesos inválidos</span><span>Revisão humana de trechos e páginas</span></div></div><div className="test-status">Pytest atual: <strong>6 testes aprovados</strong> · validação da matriz: <strong>sem inconsistências</strong></div></PresentationSlide>
        <PresentationSlide id="slide-11" number="11" time="2,5 minutos" title="Do questionário à evidência" label="Demonstração do MVP"><div className="demo-flow"><div><span>01</span><b>Responder</b><p>Escolher alternativas e definir pesos.</p></div><div><span>02</span><b>Comparar</b><p>Visualizar os três primeiros e o panorama.</p></div><div><span>03</span><b>Investigar</b><p>Analisar temas, radar, memória e fontes.</p></div></div><div className="live-demo-card"><div><span>fluxo real</span><b>{data.questions.length} temas · {data.candidates.length} candidaturas</b><p>O resultado é calculado pela API Python, não pelo frontend.</p></div><button type="button" onClick={onOpenDemo}>Abrir questionário real <span>→</span></button></div></PresentationSlide>
        <PresentationSlide id="slide-12" number="12" time="1 minuto" title="Conclusões e limitações" label="Contribuições, próximos passos e equipe"><div className="conclusion-columns"><div><b>Contribuições</b><span>Propostas organizadas por tema</span><span>Perguntas baseadas em diferenças documentadas</span><span>Cálculo reproduzível</span><span>Correspondência separada de cobertura</span><span>Resultado acompanhado de evidências</span></div><div><b>Limitações e próximos passos</b><span>Plano não representa todas as posições</span><span>Compatibilidade parcial envolve decisão metodológica</span><span>Dupla revisão e testes de usabilidade</span><span>Avaliação da neutralidade e compreensão</span><span>Novos ciclos eleitorais</span></div></div><div className="team-line"><b>Equipe:</b> Hallisson Lima · Rodrigo Monteiro · Lucas Kamel · Thamyres Costa · Ben-Hur Cavalcanti</div><div className="closing-card"><p>O Voto Consciente Pernambuco não diz em quem votar.<br /><em>Ele mostra como o resultado foi construído.</em></p><button type="button" onClick={onOpenDemo}>Demonstrar o MVP →</button></div></PresentationSlide>
      </div>
    </section>
  );
}

function PresentationSlide({ id, number, time, title, label, children }) { return <section className="deck-slide" id={id}><div className="slide-meta"><b>{number}</b><span>{label}</span><em>{time}</em></div><h2>{title}</h2><div className="slide-body">{children}</div></section>; }
function ArchNode({ icon, title, text }) { return <div className="arch-node"><span>{icon}</span><b>{title}</b><small>{text}</small></div>; }

function Questionnaire({ data, answers, weights, setAnswer, setWeights, answeredCount, onCalculate, submitting, error }) {
  return (
    <section className="workspace questionnaire-section" id="questionario">
      <div className="section-heading"><div><p className="eyebrow">01 / Questionário</p><h2>O que importa para você?</h2></div><div className="progress-copy"><strong>{answeredCount}</strong> de {data.questions.length} respondidos<div className="progress-track"><span style={{ width: `${(answeredCount / data.questions.length) * 100}%` }} /></div></div></div>
      <div className="notice"><span className="notice-icon">i</span><span>Aqui você não está escolhendo uma candidatura. Está indicando quais propostas mais se aproximam das suas prioridades.</span><b>Suas escolhas não saem deste dispositivo.</b></div>
      <details className="methodology-note" id="metodo"><summary>Como o resultado é calculado</summary><p>O Índice de Correspondência Temática compara sua resposta com as evidências classificadas de cada candidatura. Temas importantes pesam mais; temas sem evidência aparecem na cobertura e não são tratados como discordância.</p><span>O resultado não avalia caráter, viabilidade ou cumprimento das propostas.</span></details>
      <div className="questions-list">
        {data.questions.map((question, index) => (
          <article className={`question-card ${answers[question.id] !== 'NO_OPINION' ? 'is-answered' : ''}`} key={question.id}>
            <div className="question-meta"><span className="question-number">0{index + 1}</span><span className="theme-label">{question.theme}</span><span className="answer-status">{answers[question.id] !== 'NO_OPINION' ? 'Respondido' : 'Pendente'}</span></div>
            <h3>{question.text}</h3>
            <div className="option-list">
              {question.options.map((option) => <button type="button" className={`option ${answers[question.id] === option.id ? 'selected' : ''}`} onClick={() => setAnswer(question.id, option.id)} key={option.id}><span className="option-letter">{option.id}</span><span>{option.text}</span><span className="check">✓</span></button>)}
              <button type="button" className={`option neutral ${answers[question.id] === NO_OPINION ? 'selected' : ''}`} onClick={() => setAnswer(question.id, NO_OPINION)}><span className="option-letter">—</span><span>Não tenho opinião formada</span><span className="check">✓</span></button>
            </div>
            <div className="weight-row"><span>Quanto este tema pesa para você?</span><div className="weight-control">{[1, 2, 3].map((weight) => <button type="button" className={weights[question.id] === weight ? 'active' : ''} onClick={() => setWeights((current) => ({ ...current, [question.id]: weight }))} key={weight}>{WEIGHT_LABELS[weight]}</button>)}</div></div>
          </article>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
      <div className="submit-row"><span>Você poderá revisar o resultado por tema e por candidatura.</span><button className="primary-button" type="button" onClick={onCalculate} disabled={submitting}>{submitting ? 'Calculando...' : 'Ver minha correspondência'} <span>→</span></button></div>
    </section>
  );
}

function ResultsView({ results, candidates, selectedId, setSelectedId, openId, setOpenId, onRestart }) {
  const top = results.slice(0, 3);
  const selected = results.find((result) => result.candidate_id === selectedId) || results[0];
  const selectedCandidate = candidates[selected.candidate_id];
  const allThemes = [...new Set(results.flatMap((result) => result.details.map((detail) => detail.theme)))];
  return (
    <section className="workspace results-section">
      <div className="result-head"><div><p className="eyebrow">02 / Sua leitura</p><h2>O mapa das suas escolhas</h2><p className="subheading">Ordenamos as candidaturas pela proximidade com suas respostas. A cobertura mostra quanto do seu recorte tem evidência classificada.</p></div><button className="secondary-button" type="button" onClick={onRestart}>← Refazer respostas</button></div>
      <div className="top-results">{top.map((result, index) => <CandidateCard key={result.candidate_id} result={result} candidate={candidates[result.candidate_id]} position={index + 1} />)}</div>
      <div className="chart-panel"><div className="panel-heading"><div><p className="eyebrow">Panorama</p><h3>Todas as candidaturas</h3></div><span className="legend"><i /> correspondência <i className="coverage-dot" /> cobertura parcial</span></div><div className="bar-chart">{results.map((result) => <div className="bar-row" key={result.candidate_id}><span className="bar-name">{result.name}</span><div className="bar-track"><span className="bar-fill" style={{ width: `${result.score}%` }} /><span className="bar-value">{result.score.toFixed(1)}%</span></div></div>)}</div></div>
      <div className="detail-grid"><div className="theme-panel"><div className="panel-heading"><div><p className="eyebrow">Comparação</p><h3>Por tema</h3></div></div>{allThemes.map((theme) => <div className="theme-row" key={theme}><span>{theme}</span><div className="theme-bars">{top.map((result, index) => { const detail = result.details.find((item) => item.theme === theme); return <span key={result.candidate_id} title={`${result.name}: ${detail?.theme_score ?? 'sem evidência'}%`} className={`theme-bar theme-${index}`} style={{ height: `${detail?.theme_score || 4}%` }} />; })}</div></div>)}<div className="theme-key">{top.map((result, index) => <span key={result.candidate_id}><i className={`theme-key-${index}`} />{result.name}</span>)}</div></div><div className="focus-panel"><div className="panel-heading"><div><p className="eyebrow">Investigação</p><h3>Escolha uma candidatura</h3></div><select value={selected.candidate_id} onChange={(event) => setSelectedId(event.target.value)}>{results.map((result) => <option value={result.candidate_id} key={result.candidate_id}>{result.name}</option>)}</select></div><div className="focus-identity"><div className="avatar large">{selectedCandidate.photo_url ? <img src={selectedCandidate.photo_url} alt={`Foto de ${selectedCandidate.name}`} /> : initials(selected.name)}</div><div><h4>{selected.name}</h4><p>{selected.party} · número {selectedCandidate.number}</p></div><strong>{selected.score.toFixed(1)}<small>% ICT</small></strong></div><RadarChart result={selected} /><div className="focus-stats"><span><strong>{selected.coverage.toFixed(0)}%</strong> cobertura</span><span><strong>{selected.answered_with_evidence}/{selected.answered_questions}</strong> temas com evidência</span></div><p className="memory">Pontos obtidos <b>{selected.numerator.toFixed(1)}</b> de <b>{selected.denominator.toFixed(1)}</b> possíveis nas evidências classificadas.</p><div className="source-links"><a className="source-link" href={selectedCandidate.local_plan_url} target="_blank" rel="noreferrer">Abrir plano analisado ↗</a><a className="source-link" href={selectedCandidate.official_data_url} target="_blank" rel="noreferrer">Consultar dados no TSE ↗</a><small>Documento: {selectedCandidate.plan_document}</small></div></div></div>
      <div className="all-results"><div className="panel-heading"><div><p className="eyebrow">Transparência</p><h3>Memória de cálculo</h3></div><span className="small-note">Abra uma candidatura para ver os detalhes por tema</span></div>{results.map((result, index) => <ResultAccordion key={result.candidate_id} result={result} candidate={candidates[result.candidate_id]} position={index + 1} open={openId === result.candidate_id} onToggle={() => setOpenId(openId === result.candidate_id ? null : result.candidate_id)} />)}</div><div className="disclaimer"><strong>Uma leitura, não uma indicação.</strong> O resultado considera somente o conteúdo dos planos de governo analisados. Não avalia qualidade, viabilidade ou cumprimento das propostas.</div>
    </section>
  );
}

function CandidateCard({ result, candidate, position }) {
  return <article className={`candidate-card rank-${position}`}><div className="rank">0{position}</div><div className="avatar">{candidate.photo_url ? <img src={candidate.photo_url} alt={`Foto de ${candidate.name}`} /> : initials(result.name)}</div><div className="candidate-info"><h3>{result.name}</h3><p>{result.party} · {candidate.number}</p><div className="mini-progress"><span style={{ width: `${result.score}%` }} /></div></div><div className="candidate-score"><strong>{result.score.toFixed(1)}<small>%</small></strong><span>correspondência</span><em>{result.coverage.toFixed(0)}% cobertura</em></div></article>;
}

function RadarChart({ result }) {
  const details = result.details.filter((detail) => detail.similarity !== null);
  if (!details.length) return <div className="radar-empty">Sem evidência classificada para desenhar o radar.</div>;

  const size = 300;
  const center = size / 2;
  const radius = 91;
  const angle = (index) => -Math.PI / 2 + (index * Math.PI * 2) / details.length;
  const point = (index, value) => {
    const currentAngle = angle(index);
    const distance = radius * (value / 100);
    return `${center + Math.cos(currentAngle) * distance},${center + Math.sin(currentAngle) * distance}`;
  };
  const polygon = (level) => details.map((_, index) => point(index, level)).join(' ');
  const scores = details.map((detail, index) => point(index, detail.theme_score));

  return <div className="radar-chart" role="img" aria-label={`Radar de correspondência por tema para ${result.name}`}><svg viewBox={`0 0 ${size} ${size}`} aria-hidden="true"><polygon className="radar-grid" points={polygon(100)} /><polygon className="radar-grid" points={polygon(66)} /><polygon className="radar-grid" points={polygon(33)} /><line className="radar-axis" x1={center} y1={center - radius} x2={center} y2={center + radius} /><line className="radar-axis" x1={center - radius} y1={center} x2={center + radius} y2={center} /><polygon className="radar-area" points={scores.join(' ')} /><polyline className="radar-line" points={`${scores.join(' ')} ${scores[0]}`} />{scores.map((coordinate, index) => <circle className="radar-point" cx={coordinate.split(',')[0]} cy={coordinate.split(',')[1]} r="4" key={details[index].question_id} />)}</svg><div className="radar-labels">{details.map((detail, index) => <span key={detail.question_id} style={{ '--radar-angle': `${(index * 360) / details.length}deg` }}>{detail.theme}<b>{detail.theme_score.toFixed(0)}%</b></span>)}</div></div>;
}

function ResultAccordion({ result, candidate, position, open, onToggle }) {
  return <div className={`result-accordion ${open ? 'open' : ''}`}><button type="button" className="accordion-trigger" onClick={onToggle}><span className="rank-small">0{position}</span><span className="accordion-name"><b>{result.name}</b><small>{result.party} · {candidate.number}</small></span><span className="accordion-score"><b>{result.score.toFixed(1)}%</b><small>{result.coverage.toFixed(0)}% cobertura</small></span><span className="chevron">⌄</span></button>{open && <div className="accordion-body"><div className="accordion-links"><a href={candidate.local_plan_url} target="_blank" rel="noreferrer">Abrir plano analisado ↗</a><a href={candidate.official_data_url} target="_blank" rel="noreferrer">Consultar dados no TSE ↗</a></div><p className="document-note">Documento analisado: <b>{candidate.plan_document}</b>. A evidência abaixo informa a página ou seção registrada na matriz.</p>{result.details.map((detail) => <div className="detail-item" key={detail.question_id}><div><b>{detail.theme}</b><p>{detail.summary || 'Não foi localizada evidência classificada para este tema.'}</p>{detail.source && <small>{detail.source} · {detail.page}</small>}</div><span className={detail.similarity === null ? 'missing' : ''}>{detail.similarity === null ? 'Sem evidência' : `${(detail.similarity * 100).toFixed(0)}%`}</span></div>)}</div>}</div>;
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
