export default function SlideChart({ items }) {
  return <div className="slide-chart" role="img" aria-label={items.map((item) => `${item.label}: ${item.value}%`).join('; ')}>{items.map((item) => <div className="slide-chart-row" key={item.label}><span>{item.label}</span><div><i style={{ '--bar-value': `${item.value}%` }} /></div><strong>{item.value.toFixed(1).replace('.', ',')}%</strong></div>)}</div>;
}
