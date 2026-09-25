export const PRESENTATION_DATA = Object.freeze({
  candidacies: 7,
  officialPlans: 7,
  analyzedPages: 311,
  themes: 7,
  publishedQuestions: 7,
  // Valores atualizados e validados pela equipe para a apresentação em 25/09/2026.
  // Conferir sincronização posterior com data/research_evidence.json.
  researchParticipants: 136,
});

export const RESEARCH_RESULTS = Object.freeze([
  { label: 'conhecem pouco ou apenas algumas candidaturas', value: 79.4 },
  { label: 'dizem conhecer poucas propostas das candidaturas', value: 40.4 },
]);

export const PUBLIC_SITE_URL = (
  import.meta.env.VITE_PUBLIC_SITE_URL || window.location.origin
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
