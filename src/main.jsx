import { StrictMode, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { apiUrl } from './api';
import Presentation from './presentation/Presentation';
import { PRESENTATION_RETURN_SLIDE_ID, presentationUrl } from './presentation/presentationData';
import './styles.css';

const NO_OPINION = 'NO_OPINION';
const WEIGHT_LABELS = { 1: 'Normal', 2: 'Importante', 3: 'Prioridade máxima' };
const WEIGHT_EXPLANATIONS = { 1: 'importância comum', 2: 'vale duas vezes mais', 3: 'vale três vezes mais' };
const METHODOLOGY_NOTICE = 'Um agente de IA generativa apoiou a preparação inicial das informações, com supervisão da equipe. Durante o questionário, nenhuma IA é executada: o resultado é calculado por regras matemáticas fixas.';
function initials(name) {
  return name.split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase();
}

function isSafeHttpUrl(value) {
  if (typeof value !== 'string' || value.includes(' ')) return false;
  try { return ['http:', 'https:'].includes(new URL(value).protocol); } catch { return false; }
}

function ExternalLink({ href, children, className = '' }) {
  if (!isSafeHttpUrl(href) && !(typeof href === 'string' && href.startsWith('/'))) return null;
  return <a className={className} href={href} target="_blank" rel="noopener noreferrer">{children} <span aria-hidden="true">↗</span><span className="sr-only"> (abre em nova aba)</span></a>;
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
  const [announcement, setAnnouncement] = useState('');
  const resultsSectionRef = useRef(null);
  const firstQuestionRef = useRef(null);
  const shouldRevealResults = useRef(false);
  const [shouldFocusFirstQuestion, setShouldFocusFirstQuestion] = useState(false);

  useEffect(() => {
    fetch(apiUrl('/api/bootstrap'))
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

  useEffect(() => {
    if (!results || !shouldRevealResults.current || !resultsSectionRef.current) return;
    shouldRevealResults.current = false;
    const section = resultsSectionRef.current;
    const title = section.querySelector('h2');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#resultados`);
    setAnnouncement('Resultados calculados. Exibindo o mapa das suas escolhas.');
    window.requestAnimationFrame(() => {
      title?.focus({ preventScroll: true });
      section.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
    });
  }, [results]);

  useEffect(() => {
    if (!shouldFocusFirstQuestion || !firstQuestionRef.current) return;
    setShouldFocusFirstQuestion(false);
    const firstQuestion = firstQuestionRef.current;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#primeira-pergunta`);
    window.requestAnimationFrame(() => {
      firstQuestion.focus({ preventScroll: true });
      firstQuestion.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' });
    });
  }, [shouldFocusFirstQuestion]);

  const answeredCount = useMemo(
    () => Object.values(answers).filter((answer) => answer !== NO_OPINION).length,
    [answers],
  );

  function setAnswer(questionId, optionId) {
    setAnswers((current) => ({ ...current, [questionId]: optionId }));
  }

  function restart() {
    if (!window.confirm('Refazer o questionário e limpar todas as respostas e pesos?')) return;
    setAnswers(Object.fromEntries(data.questions.map((question) => [question.id, NO_OPINION])));
    setWeights(Object.fromEntries(data.questions.map((question) => [question.id, 2])));
    setResults(null);
    setSelectedId(null);
    setOpenId(null);
    setError('');
    setAnnouncement('');
    shouldRevealResults.current = false;
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.setTimeout(() => document.getElementById('questionario')?.scrollIntoView({ behavior: reducedMotion ? 'auto' : 'smooth', block: 'start' }), 0);
  }

  function reviewAnswers() {
    shouldRevealResults.current = false;
    setAnnouncement('');
    setResults(null);
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
  }

  async function calculate() {
    if (!answeredCount) {
      setError('Escolha pelo menos uma alternativa para calcular sua correspondência.');
      return;
    }
    setError('');
    setAnnouncement('');
    setSubmitting(true);
    try {
      const response = await fetch(apiUrl('/api/results'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers, weights }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || 'Não foi possível calcular os resultados.');
      setSelectedId(payload.results[0]?.candidate_id || null);
      shouldRevealResults.current = true;
      setResults(payload.results);
    } catch (reason) {
      shouldRevealResults.current = false;
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
        <nav className="main-nav" aria-label="Navegação principal"><a href="?modo=apresentacao">Apresentação</a><a href="#como-funciona">Como funciona</a><a href="#questionario">Questionário</a><a href="#metodo">Método</a></nav>
        <span className="edition">Pernambuco · 2026</span>
      </header>
      <section className="hero" id="top">
        <div className="hero-copy">
          <p className="eyebrow">Eleições · Pernambuco 2026</p>
          <h1>Seu voto começa<br /><em>nas suas prioridades.</em></h1>
          <p className="hero-text">Responda aos temas que importam para você e veja como suas escolhas se aproximam das propostas documentadas nos planos de governo.</p>
          <div className="hero-actions"><button className="primary-button hero-button" type="button" onClick={() => setShouldFocusFirstQuestion(true)}>Começar questionário <span aria-hidden="true">↓</span></button><a className="quiet-link" href="#como-funciona">Entenda antes de começar →</a></div>
          <div className="trust-line"><span className="trust-dot" /> Sem cadastro <span className="dot-separator">·</span> Respostas não armazenadas <span className="dot-separator">·</span> Dados oficiais</div>
        </div>
        <div className="hero-demo" aria-label="Demonstração do questionário"><div className="demo-label">Como você pensa?</div><div className="demo-card"><span className="demo-index">01 / {data.questions.length}</span><h2>Qual tema deve receber mais atenção?</h2><p>Escolha uma alternativa que represente melhor a sua prioridade.</p><div className="demo-options"><span className="demo-option active"><i /> Saúde pública</span><span className="demo-option"><i /> Educação</span><span className="demo-option"><i /> Segurança</span></div><div className="demo-foot"><span>uma pergunta por vez</span><span>→</span></div></div></div>
      </section>

      <MethodNotice />

      <section className="how-it-works" id="como-funciona"><div className="how-intro"><p className="eyebrow">Como funciona</p><h2>Do plano<br /><em>ao resultado.</em></h2><p>Um agente de IA generativa, baseado no Gemini e supervisionado pela equipe, apoiou somente a preparação offline. A aplicação usa perguntas e matriz já estruturadas em JSON; nenhuma IA é executada durante o questionário ou o cálculo.</p></div><ol className="pipeline-steps" aria-label="Etapas de preparação e cálculo">{[['Planos oficiais do TSE', 'Documentos públicos mantidos para consulta.'], ['Agente de IA generativa supervisionado', 'Gemini em ambiente de notebook, usado antes da publicação.'], ['Organização dos temas e propostas', 'Leitura e estruturação realizadas com supervisão da equipe.'], ['Perguntas e matriz em JSON', 'Dados estruturados usados pelo MVP.'], ['Questionário', 'Respostas e pesos informados pelo usuário, sem execução de IA.'], ['Cálculo determinístico', 'Aplicação das mesmas regras matemáticas em Python.'], ['Resultados e fontes', 'Apresentação da correspondência temática.']].map(([title, description], index, steps) => <li className="pipeline-item" key={title}><span>{index + 1}</span><div><b>{title}</b><small>{description}</small></div>{index < steps.length - 1 && <i aria-hidden="true">→</i>}</li>)}</ol></section>

      {!results ? (
        <Questionnaire data={data} answers={answers} weights={weights} setAnswer={setAnswer} setWeights={setWeights} answeredCount={answeredCount} onCalculate={calculate} submitting={submitting} error={error} firstQuestionRef={firstQuestionRef} />
      ) : (
        <ResultsView results={results} candidates={candidateById} questions={data.questions} resultsRef={resultsSectionRef} selectedId={selectedId} setSelectedId={setSelectedId} openId={openId} setOpenId={setOpenId} onReview={reviewAnswers} onRestart={restart} />
      )}
      {new URLSearchParams(window.location.search).get('origem') === 'apresentacao' && <a className="return-to-presentation" href={presentationUrl(new URLSearchParams(window.location.search).get('retorno') || PRESENTATION_RETURN_SLIDE_ID)}>Voltar à apresentação</a>}
      <p className="sr-only" aria-live="polite" aria-atomic="true">{announcement}</p>
      <footer><span>VOTO CONSCIENTE</span><span>A correspondência não avalia viabilidade, qualidade ou cumprimento das propostas.</span></footer>
    </main>
  );
}

function MethodNotice() {
  return <aside className="method-notice" aria-label="Aviso metodológico"><strong>Transparência metodológica</strong><span>{METHODOLOGY_NOTICE}</span></aside>;
}

function Questionnaire({ data, answers, weights, setAnswer, setWeights, answeredCount, onCalculate, submitting, error, firstQuestionRef }) {
  return (
    <section className="workspace questionnaire-section" id="questionario">
      <div className="section-heading"><div><p className="eyebrow">01 / Questionário</p><h2>O que importa para você?</h2></div><div className="progress-copy"><strong>{answeredCount}</strong> de {data.questions.length} respondidos<div className="progress-track"><span style={{ width: `${(answeredCount / data.questions.length) * 100}%` }} /></div></div></div>
      <div className="notice"><span className="notice-icon">i</span><span>Aqui você não está escolhendo uma candidatura. Está indicando quais propostas mais se aproximam das suas prioridades.</span><b>As respostas são usadas apenas para calcular o resultado e não são armazenadas pelo sistema.</b></div>
      <section className="calculation-explainer" id="metodo" aria-labelledby="calculation-title"><h3 id="calculation-title">Como o resultado é calculado</h3><ol><li>Você escolhe uma resposta.</li><li>Você informa o quanto aquele tema é importante.</li><li>O sistema verifica quanto a resposta se aproxima das propostas documentadas.</li><li>Os pontos são somados e transformados em uma porcentagem.</li></ol><div className="calculation-tables"><div><h4>Importância do tema</h4><div className="plain-table" role="table" aria-label="Pesos de importância"><div role="row"><b>Normal · peso 1</b><span>Importância comum.</span></div><div role="row"><b>Importante · peso 2</b><span>Vale duas vezes mais.</span></div><div role="row"><b>Prioridade máxima · peso 3</b><span>Vale três vezes mais.</span></div></div></div><div><h4>Compatibilidade</h4><div className="plain-table" role="table" aria-label="Níveis de compatibilidade"><div role="row"><b>1</b><span>Corresponde diretamente.</span></div><div role="row"><b>0,5</b><span>Corresponde parcialmente.</span></div><div role="row"><b>0</b><span>Segue abordagem diferente.</span></div></div></div></div><div className="fictional-example"><b>Exemplo simples</b><span>Saúde com peso 3 e correspondência total: 3 pontos.</span><span>Transporte com peso 2 e correspondência parcial: 1 ponto.</span></div><details className="formula-details"><summary>Ver fórmula completa</summary><p><b>Em cada tema:</b> peso atribuído × compatibilidade (0, 0,5 ou 1) = pontos ponderados.</p><p><b>ICT:</b> soma dos pontos ÷ soma dos pesos válidos × 100.</p></details><ul className="calculation-caveats"><li>“Não tenho opinião” não participa do cálculo.</li><li>Ausência de evidência não significa que a candidatura seja contra.</li><li>Temas sem evidência não entram no ICT daquela candidatura; a ausência aparece separadamente na cobertura.</li><li>A porcentagem não mede qualidade, viabilidade ou chance de cumprimento.</li><li>A ferramenta mostra correspondência temática e não recomenda voto.</li></ul></section>
      <div className="questions-list">
        {data.questions.map((question, index) => (
          <article className={`question-card ${answers[question.id] !== 'NO_OPINION' ? 'is-answered' : ''}`} id={index === 0 ? 'primeira-pergunta' : undefined} ref={index === 0 ? firstQuestionRef : undefined} tabIndex={index === 0 ? -1 : undefined} aria-labelledby={`question-title-${question.id}`} key={question.id}>
            <div className="question-meta"><span className="question-number">0{index + 1}</span><span className="theme-label">{question.theme}</span><span className="answer-status">{answers[question.id] !== 'NO_OPINION' ? 'Respondido' : 'Pendente'}</span></div>
            <h3 id={`question-title-${question.id}`}>{question.text}</h3>
            <div className="option-list">
              {question.options.map((option) => <button type="button" aria-pressed={answers[question.id] === option.id} className={`option ${answers[question.id] === option.id ? 'selected' : ''}`} onClick={() => setAnswer(question.id, option.id)} key={option.id}><span className="option-letter">{option.id}</span><span>{option.text}</span><span className="check">✓<span className="sr-only"> Selecionada</span></span></button>)}
              <button type="button" className={`option neutral ${answers[question.id] === NO_OPINION ? 'selected' : ''}`} onClick={() => setAnswer(question.id, NO_OPINION)}><span className="option-letter">—</span><span>Não tenho opinião formada</span><span className="check">✓</span></button>
            </div>
            <fieldset className="weight-row"><legend>Agora diga o quanto este tema importa para você</legend><p>A importância define quanto esta resposta vai pesar no resultado.</p><div className="weight-control">{[1, 2, 3].map((weight) => <button type="button" aria-pressed={weights[question.id] === weight} aria-label={`${WEIGHT_LABELS[weight]}, peso ${weight}, ${WEIGHT_EXPLANATIONS[weight]}`} className={weights[question.id] === weight ? 'active' : ''} onClick={() => setWeights((current) => ({ ...current, [question.id]: weight }))} key={weight}><span>{WEIGHT_LABELS[weight]}</span><small>Peso {weight}</small>{weights[question.id] === weight && <b>✓ Selecionado</b>}</button>)}</div></fieldset>
          </article>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
      <div className="submit-row"><span>Você poderá revisar o resultado por tema e por candidatura.</span><button className="primary-button" type="button" onClick={onCalculate} disabled={submitting} aria-busy={submitting}>{submitting ? 'Calculando resultados…' : 'Ver minha correspondência'} <span aria-hidden="true">→</span></button></div>
    </section>
  );
}

function ResultsView({ results, candidates, questions, resultsRef, selectedId, setSelectedId, openId, setOpenId, onReview, onRestart }) {
  const top = results.slice(0, 3);
  const selected = results.find((result) => result.candidate_id === selectedId) || results[0];
  const selectedCandidate = candidates[selected.candidate_id];
  const allThemes = [...new Set(results.flatMap((result) => result.details.map((detail) => detail.theme)))];
  return (
    <section className="workspace results-section" id="resultados" ref={resultsRef}>
      <div className="result-head"><div><p className="eyebrow">02 / Sua leitura</p><h2 tabIndex="-1">O mapa das suas escolhas</h2><p className="subheading">Ordenamos as candidaturas pela proximidade com suas respostas. A cobertura mostra quanto do seu recorte tem evidência classificada.</p></div><div className="result-actions"><button className="secondary-button" type="button" onClick={onReview}>← Rever respostas</button><button className="secondary-button" type="button" onClick={onRestart}>Refazer questionário</button></div></div>
      <MethodNotice />
      <div className="result-help" aria-label="Ajuda para interpretar os resultados"><details><summary>O que significa % de correspondência?</summary><p>A correspondência mostra o quanto as propostas documentadas se aproximam das respostas consideradas no cálculo. Ela não mede se uma proposta é boa, viável ou se será cumprida.</p></details><details><summary>O que significa % de cobertura?</summary><p>A cobertura mostra em quantos dos temas respondidos foram encontradas evidências classificadas no plano do candidato. Uma cobertura menor significa que havia menos temas disponíveis para comparação.</p></details><details><summary>Como ler os dois indicadores juntos?</summary><p>Leia sempre os dois números juntos. Uma correspondência alta com cobertura baixa pode significar que houve boa aproximação em poucos temas. Uma cobertura alta indica que mais respostas puderam ser comparadas.</p></details></div>
      <div className="top-results">{top.map((result, index) => <CandidateCard key={result.candidate_id} result={result} candidate={candidates[result.candidate_id]} position={index + 1} />)}</div>
      <div className="chart-panel"><div className="panel-heading"><div><p className="eyebrow">Panorama</p><h3>Todas as candidaturas</h3></div><span className="legend"><i /> correspondência <i className="coverage-dot" /> cobertura parcial</span></div><div className="bar-chart">{results.map((result) => <div className="bar-row" key={result.candidate_id}><span className="bar-name">{result.name}</span><div className="bar-track"><span className="bar-fill" style={{ width: `${result.score}%` }} /><span className="bar-value">{result.score.toFixed(1)}%</span></div></div>)}</div></div>
      <div className="detail-grid"><ThemeComparison themes={allThemes} results={top} candidates={candidates} /><div className="focus-panel"><div className="panel-heading"><div><p className="eyebrow">Investigação</p><h3>Escolha uma candidatura</h3></div><select value={selected.candidate_id} onChange={(event) => setSelectedId(event.target.value)}>{results.map((result) => <option value={result.candidate_id} key={result.candidate_id}>{result.name}</option>)}</select></div><div className="focus-identity"><div className="avatar large">{selectedCandidate.photo_url ? <img src={selectedCandidate.photo_url} alt={`Foto de ${selectedCandidate.name}`} /> : initials(selected.name)}</div><div><h4>{selected.name}</h4><p>{selected.party} · número {selectedCandidate.number}</p></div><strong>{selected.score.toFixed(1)}<small>% ICT</small></strong></div><RadarChart result={selected} /><div className="focus-stats"><span><strong>{selected.coverage.toFixed(0)}%</strong> cobertura</span><span><strong>{selected.answered_with_evidence}/{selected.answered_questions}</strong> temas com evidência</span></div><p className="memory">Pontos obtidos <b>{selected.numerator.toFixed(1)}</b> de <b>{selected.denominator.toFixed(1)}</b> possíveis nas evidências classificadas.</p><div className="source-links"><ExternalLink className="source-link" href={selectedCandidate.local_plan_url}>Abrir plano analisado</ExternalLink><ExternalLink className="source-link" href={selectedCandidate.official_data_url}>Consultar dados no TSE</ExternalLink><small>Documento: {selectedCandidate.plan_document}</small></div></div></div>
      <div className="all-results"><div className="panel-heading"><div><p className="eyebrow">Transparência</p><h3>Memória de cálculo</h3></div><span className="small-note">Abra uma candidatura para ver resposta, peso, compatibilidade, pontos e fonte</span></div>{results.map((result, index) => <ResultAccordion key={result.candidate_id} result={result} candidate={candidates[result.candidate_id]} questions={questions} position={index + 1} open={openId === result.candidate_id} onToggle={() => setOpenId(openId === result.candidate_id ? null : result.candidate_id)} />)}</div><div className="disclaimer"><strong>Uma leitura, não uma indicação.</strong> O resultado considera somente o conteúdo dos planos de governo analisados. Não avalia qualidade, viabilidade ou cumprimento das propostas.</div>
    </section>
  );
}

function ThemeComparison({ themes, results, candidates }) {
  return <div className="theme-panel"><div className="panel-heading theme-heading"><div><p className="eyebrow">Comparação</p><h3>Por tema</h3><p className="theme-explanation">Os valores mostram a correspondência em cada tema. Ausência de evidência não significa posição contrária.</p></div></div><div className="theme-list">{themes.map((theme) => <div className="theme-row" key={theme}><span className="theme-name">{theme}</span><div className="theme-bars">{results.map((result, index) => { const detail = result.details.find((item) => item.theme === theme); const candidate = candidates[result.candidate_id]; const missingEvidence = detail?.similarity === null; const notConsidered = !detail; const value = notConsidered ? 'Não considerado' : missingEvidence ? 'Sem evidência' : `${detail.theme_score.toFixed(0)}%`; const accessibleValue = notConsidered ? 'não considerado' : missingEvidence ? 'sem evidência localizada' : `${detail.theme_score.toFixed(0)}% de correspondência`; return <div className={`theme-candidate${missingEvidence ? ' is-missing' : ''}${notConsidered ? ' is-not-considered' : ''}`} key={result.candidate_id} role="img" aria-label={`${result.name}, ${theme}, ${accessibleValue}`}><div className="theme-plot"><img src={candidate.photo_url} alt="" aria-hidden="true" /><div className="theme-bar-stage" aria-hidden="true"><span className="theme-value">{value}</span>{!notConsidered && <span className={`theme-bar theme-${index}`} style={missingEvidence ? undefined : { '--theme-score': detail.theme_score }} />}</div></div><small>{result.name}</small></div>; })}</div></div>)}</div></div>;
}

function CandidateCard({ result, candidate, position }) {
  const links = (candidate.social_links || []).filter((link) => isSafeHttpUrl(link.url));
  return <article className={`candidate-card rank-${position}`}><div className="rank"><span className="sr-only">Posição </span>{position}º</div><div className="candidate-photo">{candidate.photo_url ? <img src={candidate.photo_url} alt={`Foto de ${candidate.name}`} /> : initials(result.name)}</div><div className="candidate-info"><h3>{result.name}</h3><p>{result.party} · número {candidate.number}</p><div className="mini-progress"><span style={{ width: `${result.score}%` }} /></div></div><div className="candidate-score"><strong>{result.score.toFixed(1)}<small>%</small></strong><span>correspondência</span><em>{result.coverage.toFixed(0)}% cobertura</em></div><div className="candidate-links"><ExternalLink href={candidate.local_plan_url}>Plano analisado</ExternalLink><ExternalLink href={candidate.official_data_url}>Consulta no TSE</ExternalLink>{links.map((link) => <ExternalLink href={link.url} key={`${link.label}-${link.url}`}>{link.label}</ExternalLink>)}{!links.length && <small>Nenhum canal oficial válido informado na fonte consultada.</small>}</div></article>;
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

function ResultAccordion({ result, candidate, questions, position, open, onToggle }) {
  const questionById = Object.fromEntries(questions.map((question) => [question.id, question]));
  return <div className={`result-accordion ${open ? 'open' : ''}`}><button type="button" className="accordion-trigger" onClick={onToggle}><span className="rank-small">0{position}</span><span className="accordion-name"><b>{result.name}</b><small>{result.party} · {candidate.number}</small></span><span className="accordion-score"><b>{result.score.toFixed(1)}% ICT</b><small>{result.coverage.toFixed(0)}% cobertura</small></span><span className="chevron">⌄</span></button>{open && <div className="accordion-body"><div className="accordion-links"><a href={candidate.local_plan_url} target="_blank" rel="noreferrer">Abrir plano analisado (nova aba) ↗</a><a href={candidate.official_data_url} target="_blank" rel="noreferrer">Consultar fonte oficial no TSE (nova aba) ↗</a></div><p className="document-note">Documento analisado: <b>{candidate.plan_document}</b>. A evidência abaixo informa a página ou seção registrada na matriz.</p>{result.details.map((detail) => { const question = questionById[detail.question_id]; const choice = question?.options.find((option) => option.id === detail.chosen_option); return <div className="detail-item" key={detail.question_id}><div><b>{detail.theme}</b><p className="calculation-line"><strong>Resposta escolhida:</strong> {detail.chosen_option}{choice ? ` — ${choice.text}` : ''}</p><p>{detail.summary || 'Não foi localizada evidência classificada para este tema.'}</p>{detail.source && <small>{detail.source} · {detail.page}</small>}</div><div className={`detail-math ${detail.similarity === null ? 'missing' : ''}`}>{detail.similarity === null ? <span>Sem evidência<br />fora do ICT</span> : <><span>Peso <b>{detail.weight}</b></span><span>Compatibilidade <b>{detail.similarity.toFixed(1).replace('.', ',')}</b></span><span>Pontos ponderados <b>{detail.points.toFixed(1).replace('.', ',')}</b></span></>}</div></div>; })}<p className="result-formula">Soma dos pontos: <b>{result.numerator.toFixed(1)}</b> · Soma dos pesos válidos: <b>{result.denominator.toFixed(1)}</b> · ICT final: <b>{result.score.toFixed(1)}%</b> · Cobertura: <b>{result.coverage.toFixed(0)}%</b></p></div>}</div>;
}

const presentationMode = new URLSearchParams(window.location.search).get('modo') === 'apresentacao';
createRoot(document.getElementById('root')).render(<StrictMode>{presentationMode ? <Presentation /> : <App />}</StrictMode>);
