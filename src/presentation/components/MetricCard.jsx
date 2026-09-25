export default function MetricCard({ value, label, detail }) {
  return <div className="presentation-metric"><strong>{value}</strong><span>{label}</span>{detail && <small>{detail}</small>}</div>;
}
