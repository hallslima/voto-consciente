import questions from '../../data/questions.json';
import researchEvidence from '../../data/research_evidence.json';

function researchResult(id) {
  const result = researchEvidence.results.find((item) => item.id === id);
  if (!result) throw new Error(`Indicador oficial da pesquisa não encontrado: ${id}`);
  return Object.freeze({ label: result.indicator, value: result.percentage });
}

const healthQuestion = questions.find((question) => question.id === 'q1_saude');
if (!healthQuestion) throw new Error('Pergunta oficial de saúde não encontrada.');

export const PRESENTATION_DATA = Object.freeze({
  candidacies: 7,
  officialPlans: 7,
  analyzedPages: 311,
  themes: 7,
  publishedQuestions: 7,
  researchParticipants: researchEvidence.sample_size,
});

export const RESEARCH_RESULTS = Object.freeze([
  researchResult('candidate_awareness'),
  researchResult('proposal_awareness'),
]);

export const HEALTH_QUESTION = Object.freeze(healthQuestion);

export const PUBLIC_SITE_URL = (
  import.meta.env.VITE_PUBLIC_SITE_URL || 'https://voto-consciente.netlify.app/'
).replace(/\/$/, '');

export const DEMO_SLIDE_ID = 'demo';

export function presentationUrl(slideId = DEMO_SLIDE_ID) {
  const url = new URL(window.location.href);
  url.search = '';
  url.searchParams.set('modo', 'apresentacao');
  url.searchParams.set('slide', slideId);
  url.hash = '';
  return url.toString();
}

export function mvpUrl({ fromPresentation = false } = {}) {
  const url = new URL(PUBLIC_SITE_URL);
  url.search = '';
  url.hash = '';
  if (fromPresentation) {
    url.searchParams.set('origem', 'apresentacao');
    url.searchParams.set('retorno', DEMO_SLIDE_ID);
  }
  return url.toString();
}
