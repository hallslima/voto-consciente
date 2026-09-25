import PresentationQRCode from './components/PresentationQRCode';

export default function Slide({ slide, number, total, children, print = false }) {
  return (
    <article
      className={`presentation-slide presentation-slide--${slide.id}${print ? ' presentation-slide--print' : ''}`}
      aria-labelledby={`${slide.id}-title${print ? '-print' : ''}`}
      data-slide-id={slide.id}
    >
      <header className="slide-kicker"><span>{slide.section}</span><span>{String(number).padStart(2, '0')} / {total}</span></header>
      <div className="slide-content">{children}</div>
      <footer className="slide-footer"><span>Voto Consciente Pernambuco</span><PresentationQRCode compact /></footer>
    </article>
  );
}
