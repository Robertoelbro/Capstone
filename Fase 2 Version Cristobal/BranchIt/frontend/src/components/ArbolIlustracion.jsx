/**
 * Ilustración decorativa del "árbol profesional": un SVG simple en
 * tonos verdes de marca, sin depender de imágenes externas.
 */
export default function ArbolIlustracion({ className = "" }) {
  return (
    <svg viewBox="0 0 200 180" className={className} role="presentation" aria-hidden="true">
      <rect x="92" y="110" width="16" height="60" rx="4" fill="#8B5E34" />
      <circle cx="100" cy="95" r="55" fill="#3B703D" opacity="0.15" />
      <circle cx="70" cy="80" r="34" fill="#4C8C4C" opacity="0.9" />
      <circle cx="130" cy="80" r="34" fill="#4C8C4C" opacity="0.9" />
      <circle cx="100" cy="55" r="38" fill="#3B703D" />
      <circle cx="78" cy="95" r="22" fill="#66AC66" opacity="0.85" />
      <circle cx="122" cy="95" r="22" fill="#66AC66" opacity="0.85" />
    </svg>
  );
}
