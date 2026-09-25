export default function SlideFlow({ steps }) {
  return <ol className="slide-flow" aria-label="Fluxo de preparação dos dados">{steps.map((step, index) => <li key={step}><span>{String(index + 1).padStart(2, '0')}</span><b>{step}</b>{index < steps.length - 1 && <i aria-hidden="true">→</i>}</li>)}</ol>;
}
