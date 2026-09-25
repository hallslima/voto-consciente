import { QRCodeSVG } from 'qrcode.react';
import { PUBLIC_SITE_URL, mvpUrl } from '../presentationData';

export default function PresentationQRCode({ compact = false, large = false }) {
  const size = large ? 132 : compact ? 54 : 88;
  return <a className={`presentation-qr${large ? ' presentation-qr--large' : ''}`} href={mvpUrl()} aria-label={`Acesse o MVP em ${PUBLIC_SITE_URL}`}><span className="qr-image" aria-hidden="true"><QRCodeSVG value={mvpUrl()} size={size} level="M" bgColor="#ffffff" fgColor="#19332e" marginSize={2} /></span><span>Acesse o MVP<small>{large ? PUBLIC_SITE_URL : ''}</small></span></a>;
}
