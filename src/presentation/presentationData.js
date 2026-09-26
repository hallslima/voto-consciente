import researchEvidence from '../../data/research_evidence.json';

function researchResult(id) {
  const result = researchEvidence.results.find((item) => item.id === id);
  if (!result) throw new Error(`Indicador oficial da pesquisa não encontrado: ${id}`);
  return Object.freeze({ label: result.indicator, value: result.percentage });
}

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

export const PUBLIC_SITE_URL = (
  import.meta.env.VITE_PUBLIC_SITE_URL || 'https://voto-consciente.netlify.app/'
).replace(/\/$/, '');

export const PRESENTATION_RETURN_SLIDE_ID = 'conclusao';

export function presentationUrl(slideId = PRESENTATION_RETURN_SLIDE_ID) {
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
    url.searchParams.set('retorno', PRESENTATION_RETURN_SLIDE_ID);
  }
  return url.toString();
}
