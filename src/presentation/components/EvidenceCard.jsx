export default function EvidenceCard({ context, title, identification, metrics, note, detail, href }) {
  return (
    <article className="evidence-card">
      <header className="evidence-card__header">
        <span className="evidence-card__context">{context}</span>
        <h3>{title}</h3>
        {identification && <p>{identification}</p>}
      </header>
      <div className="evidence-card__metrics">
        {metrics.map((metric) => (
          <div className="evidence-metric" key={metric.value}>
            <strong>{metric.value}</strong>
            <span>{metric.label}</span>
          </div>
        ))}
      </div>
      <footer className="evidence-card__source">
        {detail && <p>{detail}</p>}
        <p>{note}</p>
        {href && (
          <a href={href} target="_blank" rel="noopener noreferrer" aria-label={`Ler reportagem sobre ${title} (abre em nova aba)`}>
            Ler reportagem <span aria-hidden="true">↗</span>
          </a>
        )}
      </footer>
    </article>
  );
}
