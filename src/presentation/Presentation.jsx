import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import EvidenceCard from './components/EvidenceCard';
import MetricCard from './components/MetricCard';
import PresentationQRCode from './components/PresentationQRCode';
import SlideFlow from './components/SlideFlow';
import Slide from './Slide';
import { mvpUrl, PRESENTATION_DATA as metrics, PUBLIC_SITE_URL, RESEARCH_RESULTS } from './presentationData';
import { slides } from './slides';
import './Presentation.css';

const FLOW = ['Planos oficiais do TSE', 'Agente de IA generativa supervisionado', 'Organização dos temas e propostas', 'Perguntas e matriz em JSON', 'Questionário', 'Cálculo determinístico', 'Resultados e fontes'];
const TEAM = ['Ben-hur Queiroz', 'Hallisson Lima', 'Lucas Kamel', 'Rodrigo Monteiro', 'Thamyres Costa'];
const INTERACTIVE_SELECTOR = 'button, a, input, select, textarea, summary, details, [role="button"], [contenteditable="true"]';

function Heading({ slide, children }) {
  return <h1 id={`${slide.id}-title`}>{children || slide.title}</h1>;
}

function SlideContent({ slide, revealStep = 0 }) {
  switch (slide.id) {
    case 'capa': return <div className="cover-layout"><div><p className="slide-eyebrow">MBA em Ciência de Dados e Inteligência Artificial</p><h1 id="capa-title">Voto Consciente<br /><em>Pernambuco</em></h1><p className="slide-lead">Comparação transparente entre as prioridades do eleitor e os planos de governo</p><p className="institution">Faculdade SENAC Pernambuco | 2026</p></div><div className="team-card"><span>Equipe</span>{TEAM.map((name) => <b key={name}>{name}</b>)}</div></div>;
    case 'pergunta-candidaturas': return <div className="audience-question"><Heading slide={slide}>Você sabe quantos candidatos concorrem ao Governo de Pernambuco nesta eleição?</Heading><div className={`reveal-panel${revealStep ? ' is-revealed' : ''}`} aria-hidden={!revealStep}><strong>{metrics.candidacies}</strong><span>candidaturas deferidas no recorte atual</span></div></div>;
    case 'pergunta-leitura': return <div className="audience-question"><Heading slide={slide}>Você já decidiu em quem pretende votar com base na leitura do plano de governo completo?</Heading><blockquote className={`reveal-quote${revealStep ? ' is-revealed' : ''}`} aria-hidden={!revealStep}>Decidir o voto é diferente de conhecer o documento oficial da candidatura.</blockquote></div>;
    case 'pergunta-comparacao': return <div className="audience-question"><Heading slide={slide}>Você conseguiria comparar esse plano com todos os demais planos registrados?</Heading><div className={`reveal-metrics metric-grid metric-grid--two${revealStep ? ' is-revealed' : ''}`} aria-hidden={!revealStep}><MetricCard value={metrics.officialPlans} label="planos oficiais" /><MetricCard value={metrics.analyzedPages} label="páginas analisadas" /><small>Fonte dos documentos: Tribunal Superior Eleitoral (TSE).</small></div></div>;
    case 'escala': return <><Heading slide={slide} /><div className="metric-grid metric-grid--three"><MetricCard value={metrics.candidacies} label="candidaturas" /><MetricCard value={metrics.analyzedPages} label="páginas" /><MetricCard value="horas" label="de leitura e comparação" /></div><div className="callout">Em uma eleição completa, o eleitor ainda precisa lidar com centenas de candidaturas para diferentes cargos.</div><p className="scope-note">O MVP atual analisa somente candidaturas ao Governo de Pernambuco. Deputados não fazem parte deste recorte.</p></>;
    case 'problema': return <><Heading slide={slide} /><div className="problem-grid">{[['▤', 'Planos extensos'], ['≠', 'Documentos pouco padronizados'], ['⇄', 'Comparação difícil'], ['?', 'Candidaturas pouco conhecidas'], ['⌕', 'Propostas difíceis de localizar no TSE']].map(([icon, label]) => <div key={label}><span aria-hidden="true">{icon}</span><b>{label}</b></div>)}</div></>;
    case 'evidencias': return <><Heading slide={slide} /><p className="evidence-subtitle">Três recortes distintos, apresentados sem generalização</p><div className="evidence-grid"><EvidenceCard context="Pesquisa realizada pelo projeto" title="Pesquisa do grupo" identification={`${metrics.researchParticipants} participantes`} metrics={RESEARCH_RESULTS.map((item) => ({ value: `${item.value.toFixed(1).replace('.', ',')}%`, label: item.label }))} note="Pesquisa exploratória realizada com uma amostra por conveniência. Os resultados ajudam a compreender o grupo participante, mas não representam todo o eleitorado de Pernambuco." /><EvidenceCard context="Fonte externa · Rio de Janeiro" title="Pesquisa Quaest no Rio de Janeiro" metrics={[{ value: '69%', label: 'se dizem indecisos sobre o voto para governador' }, { value: '88%', label: 'se dizem indecisos sobre o voto para o Senado' }]} note="Fonte externa referente ao Rio de Janeiro. Os resultados não representam Pernambuco." href="https://g1.globo.com/rj/rio-de-janeiro/eleicoes/2026/noticia/2026/08/26/quaest-no-rj-indecisos-sobre-o-voto.ghtml" /><EvidenceCard context="Contexto histórico · Brasil" title="Pesquisa nacional citada em 2018" metrics={[{ value: '59%', label: 'dos brasileiros não sabiam em quem votar ou declaravam intenção de votar em branco ou nulo' }]} note="Dado nacional usado como contexto histórico de 2018. Não representa Pernambuco em 2026." href="https://veja.abril.com.br/politica/59-dos-brasileiros-nao-sabem-em-quem-irao-votar-ou-anularao-o-voto/" /></div></>;
    case 'objetivo': return <><Heading slide={slide} /><div className="research-block"><div><span>Pergunta de pesquisa</span><b>Como uma ferramenta baseada em dados públicos pode ajudar o eleitor a comparar suas prioridades com propostas verificáveis?</b></div><div><span>Objetivo</span><b>Relacionar as prioridades do eleitor com propostas documentadas nos planos de governo.</b></div></div><p className="ethics-banner">O projeto mostra correspondência temática. Não indica em quem votar.</p></>;
    case 'dados': return <><Heading slide={slide} /><div className="metric-grid metric-grid--data"><MetricCard value={metrics.candidacies} label="candidaturas" /><MetricCard value={metrics.officialPlans} label="planos oficiais" /><MetricCard value={metrics.analyzedPages} label="páginas dos documentos" /><MetricCard value="TSE" label="fonte oficial" /><MetricCard value={metrics.themes} label="temas" /><MetricCard value={metrics.publishedQuestions} label="perguntas publicadas" /></div><p className="source-line">Fotos, informações eleitorais e documentos oficiais vinculados às fontes do TSE.</p></>;
    case 'preparacao': return <><Heading slide={slide}>Análise e organização com agente de IA</Heading><SlideFlow steps={FLOW} /><p className="human-note"><b>Baseado no Gemini e supervisionado pela equipe.</b> O agente foi usado apenas na preparação dos dados. O questionário e o cálculo não utilizam IA.</p></>;
    case 'perguntas': return <><Heading slide={slide} /><div className="method-steps">{[['1', 'Fonte dos dados', 'Planos oficiais disponíveis no TSE.'], ['2', 'Organização temática', `Propostas agrupadas em ${metrics.themes} temas de políticas públicas.`], ['3', 'Identificação dos contrastes', 'Diferenças documentadas sobre como cada política seria executada.'], ['4', 'Formulação', 'Alternativas baseadas nas propostas, sem nomes de candidaturas.'], ['5', 'Limite metodológico', 'A preparação inicial ocorreu fora do código e não possui rastreabilidade técnica completa.']].map(([n, title, text]) => <div key={n}><span>{n}</span><b>{title}</b><small>{text}</small></div>)}</div><div className="vaa-strip"><b>Princípios de uma VAA</b><span>Perguntas neutras</span><span>Base documental</span><span>“Não tenho opinião”</span><span>Resultado explicável</span><span>Sem indicação direta</span></div><p className="ai-boundary">O agente de IA generativa foi supervisionado pela equipe e usado somente antes da publicação. Não escolhe candidaturas, não recomenda voto e não calcula o ICT.</p></>;
    case 'arquitetura': return <><Heading slide={slide} /><div className="tech-diagram">{[['React + Vite', 'Interface, apresentação e gráficos'], ['FastAPI + Python', 'API e cálculo'], ['JSON', 'Perguntas, candidaturas e matriz'], ['Agente de IA generativa', 'Gemini em ambiente de notebook, utilizado na preparação offline dos dados'], ['Pytest', 'Testes automatizados'], ['Netlify + Render', 'Publicação do frontend e da API']].map(([title, text]) => <div key={title}><b>{title}</b><span>{text}</span></div>)}</div><p className="test-proof"><b>Suíte automatizada para cálculo, API, interface e apresentação</b></p></>;
    case 'limitacoes': return <><Heading slide={slide} /><div className="limitations-grid">{['Compara somente conteúdo documentado', 'Não avalia viabilidade jurídica, técnica ou financeira', 'Não prevê cumprimento das propostas', 'Planos têm níveis diferentes de detalhamento', 'A classificação parcial exige julgamento metodológico', 'Pesquisa própria por conveniência', 'Recorte exclusivo do Governo de Pernambuco', 'A preparação inicial ocorreu fora do código e ainda possui limitação de rastreabilidade técnica'].map((item, index) => <span key={item}><i aria-hidden="true">{String(index + 1).padStart(2, '0')}</i>{item}</span>)}</div></>;
    case 'conclusao': return <div className="closing-layout"><div className="closing-message"><Heading slide={slide} /><blockquote>O projeto não diz em quem o eleitor deve votar. Ele mostra onde as prioridades informadas encontram correspondência nos planos de governo.</blockquote><p className="closing-invitation">Aponte a câmera ou acesse o endereço para conhecer o MVP.</p><div className="closing-team">{TEAM.join(' · ')}</div></div><div className="closing-qr"><p className="closing-qr__callout">Acesse o MVP</p><PresentationQRCode url={PUBLIC_SITE_URL} /><a className="closing-qr__url" href={PUBLIC_SITE_URL}>{PUBLIC_SITE_URL}/</a><small>Não é necessário fazer cadastro.</small><a className="presentation-primary" href={mvpUrl()}>Abrir o MVP</a></div></div>;
    default: return null;
  }
}

function slideIndexFromUrl() {
  const requested = new URLSearchParams(window.location.search).get('slide');
  const index = slides.findIndex((slide) => slide.id === requested);
  return index >= 0 ? index : 0;
}

export default function Presentation() {
  const [started, setStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(slideIndexFromUrl);
  const [revealStep, setRevealStep] = useState(0);
  const [fullscreen, setFullscreen] = useState(Boolean(document.fullscreenElement));
  const [showNotes, setShowNotes] = useState(false);
  const shellRef = useRef(null);
  const current = slides[currentIndex];
  const progress = ((currentIndex + 1) / slides.length) * 100;

  const updateUrl = useCallback((index) => {
    const url = new URL(window.location.href);
    url.searchParams.set('modo', 'apresentacao');
    url.searchParams.set('slide', slides[index].id);
    window.history.replaceState(null, '', url);
  }, []);

  const goTo = useCallback((index) => {
    const bounded = Math.max(0, Math.min(slides.length - 1, index));
    setCurrentIndex(bounded);
    setRevealStep(0);
    updateUrl(bounded);
  }, [updateUrl]);

  const next = useCallback(() => {
    const maxReveal = current.revealSteps || 0;
    if (revealStep < maxReveal) setRevealStep((step) => step + 1);
    else if (currentIndex < slides.length - 1) goTo(currentIndex + 1);
  }, [current, currentIndex, goTo, revealStep]);

  const previous = useCallback(() => {
    if (revealStep > 0) setRevealStep((step) => step - 1);
    else if (currentIndex > 0) {
      const previousIndex = currentIndex - 1;
      setCurrentIndex(previousIndex);
      setRevealStep(slides[previousIndex].revealSteps || 0);
      updateUrl(previousIndex);
    }
  }, [currentIndex, revealStep, updateUrl]);

  useEffect(() => {
    const onFullscreenChange = () => setFullscreen(Boolean(document.fullscreenElement));
    document.addEventListener('fullscreenchange', onFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', onFullscreenChange);
  }, []);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (!started || event.target.closest?.(INTERACTIVE_SELECTOR)) return;
      if (event.key === 'ArrowRight' || event.key === ' ') { event.preventDefault(); next(); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); previous(); }
      if (event.key === 'Home') { event.preventDefault(); goTo(0); }
      if (event.key === 'End') { event.preventDefault(); goTo(slides.length - 1); }
      if (event.key === 'Escape' && document.fullscreenElement) document.exitFullscreen();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [goTo, next, previous, started]);

  const start = async () => {
    setStarted(true);
    updateUrl(currentIndex);
    try { await shellRef.current?.requestFullscreen?.(); } catch { /* Presentation remains usable without fullscreen permission. */ }
  };

  const toggleFullscreen = async () => {
    if (document.fullscreenElement) await document.exitFullscreen();
    else await shellRef.current?.requestFullscreen?.();
  };

  const printableSlides = useMemo(() => slides.map((slide, index) => <Slide slide={slide} number={index + 1} total={slides.length} print key={slide.id}><SlideContent slide={slide} revealStep={slide.revealSteps || 0} /></Slide>), []);

  return <main className="presentation-shell" ref={shellRef} data-testid="presentation-mode">
    {!started ? <section className="presentation-start"><div className="start-mark">VC</div><p>MBA em Ciência de Dados e Inteligência Artificial</p><h1>Voto Consciente <em>Pernambuco</em></h1><span>{slides.length} slides · até 15 minutos</span><button type="button" className="presentation-primary" onClick={start}>Iniciar apresentação</button><a href={mvpUrl()}>Voltar ao MVP</a></section> : <>
      <header className="presentation-toolbar" aria-label="Ferramentas da apresentação"><div className="presentation-toolbar__left"><a href={mvpUrl()}>Voltar ao MVP</a></div><div className="presentation-toolbar__center"><button type="button" onClick={toggleFullscreen}>{fullscreen ? 'Sair da tela cheia' : 'Entrar em tela cheia'}</button></div><div className="presentation-toolbar__right"><button type="button" onClick={() => window.print()}>Imprimir ou salvar em PDF</button></div></header>
      <div className="presentation-stage" aria-live="polite" aria-atomic="true"><div className="presentation-slide-frame"><Slide slide={current} number={currentIndex + 1} total={slides.length}><SlideContent slide={current} revealStep={revealStep} /></Slide></div></div>
      <footer className="presentation-navigation"><nav className="presentation-controls" aria-label="Navegação da apresentação"><button type="button" onClick={previous} disabled={currentIndex === 0 && revealStep === 0} aria-label="Slide ou revelação anterior">← <span>Anterior</span></button><div className="presentation-position" aria-label={`Slide ${currentIndex + 1} de ${slides.length}`}><b>{currentIndex + 1} / {slides.length}</b><div className="presentation-progress" role="progressbar" aria-valuemin="1" aria-valuemax={slides.length} aria-valuenow={currentIndex + 1}><i style={{ '--progress': `${progress}%` }} /></div></div><button type="button" className="presentation-notes-button" aria-expanded={showNotes} onClick={() => setShowNotes((visible) => !visible)}>Notas</button><button type="button" onClick={next} disabled={currentIndex === slides.length - 1 && revealStep >= (current.revealSteps || 0)} aria-label="Próximo slide ou revelação"><span>Próximo</span> →</button></nav>{showNotes && <aside className="speaker-notes"><b>Notas do apresentador</b><p>{current.notes}</p><small>Tempo sugerido: {current.estimatedSeconds} segundos</small></aside>}</footer>
      <p className="sr-only" role="status">Slide atual: {currentIndex + 1} de {slides.length}, {current.title}.</p>
    </>}
    <section className="print-deck" aria-hidden="true">{printableSlides}</section>
  </main>;
}
