import { HiOutlineSparkles } from "react-icons/hi";

/**
 * Placeholder para las secciones del sidebar que todavía no tienen
 * mockup/diseño propio (Explorar empleos, Conexiones, Mensajes, etc.).
 * Evita links rotos mientras se definen esas pantallas.
 */
export default function Proximamente({ titulo }) {
  return (
    <div className="rounded-xl2 border border-dashed border-line bg-surface p-10 flex flex-col items-center text-center gap-2 max-w-md mx-auto mt-10">
      <HiOutlineSparkles className="text-3xl text-brand-600" />
      <h1 className="font-semibold text-ink">{titulo}</h1>
      <p className="text-sm text-muted">
        Esta sección todavía no está diseñada. Próximamente vas a poder usarla desde aquí.
      </p>
    </div>
  );
}
