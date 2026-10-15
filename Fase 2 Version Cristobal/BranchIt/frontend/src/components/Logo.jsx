/** Ícono de hoja dibujado a mano (no depende de ninguna librería de íconos). */
function IconoHoja({ className }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="currentColor" aria-hidden="true">
      <path d="M12 2C6.5 2 3 6 3 11c0 6 4.5 11 9 11 .7-2 1-4 1-6-4 0-7-2-7-2s3.5 1 7 1c.2-1.3.3-2.6.3-4C13.3 7.3 12.7 4.5 12 2z" />
      <path d="M21 8c0 6.6-4 11-9 11-.7-2-1-4-1-6 4.4 0 9-2.3 9-5 0-1-.3-1.8-.3-1.8S21 7 21 8z" />
    </svg>
  );
}

/**
 * Isotipo + wordmark de BranchIt. Se usa en el sidebar y se puede
 * reutilizar en cualquier pantalla pública (login, registro, etc.).
 */
export default function Logo({ conTagline = true }) {
  return (
    <div className="flex items-center gap-2">
      <IconoHoja className="text-brand-600 w-7 h-7 shrink-0" />
      <div className="leading-tight">
        <p className="text-xl font-bold text-ink">
          Branch<span className="text-brand-600">It</span>
        </p>
        {conTagline && (
          <p className="text-[11px] text-muted -mt-0.5">Tu carrera, tu crecimiento.</p>
        )}
      </div>
    </div>
  );
}
