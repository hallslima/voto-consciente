import { QRCodeSVG } from 'qrcode.react';

export default function PresentationQRCode({ url }) {
  return <a className="presentation-qr-code" href={url} aria-label={`Abrir Voto Consciente Pernambuco em ${url}`}><QRCodeSVG value={url} size={420} level="M" bgColor="#ffffff" fgColor="#19332e" marginSize={3} /></a>;
}
