import { PiPlantBold } from "react-icons/pi";

/**
 * Widget "Mi Crecimiento" que vive al final del sidebar.
 * Muestra qué tan completo está el perfil del egresado.
 */
export default function GrowthWidget({ porcentaje = 35 }) {
  return (
    <div className="rounded-xl2 border border-line bg-surface p-4">
      <p className="text-sm font-semibold text-ink mb-3">Mi Crecimiento</p>
      <div className="flex items-center gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-brand-100 text-brand-600 text-xl">
          <PiPlantBold />
        </div>
        <div className="flex-1">
          <p className="text-xs text-muted">Perfil Completo</p>
          <p className="text-lg font-bold text-ink leading-none">{porcentaje}%</p>
        </div>
      </div>
      <div className="progreso-pista h-2 w-full mt-3">
        <div className="progreso-relleno h-full" style={{ width: `${porcentaje}%` }} />
      </div>
      <p className="text-xs text-muted mt-2">Completa tu perfil para seguir creciendo</p>
    </div>
  );
}
