import { HiOutlineEye, HiOutlineThumbUp } from "react-icons/hi";

/**
 * Tarjeta de proyecto. Se usa tanto en "Proyectos destacados de la
 * comunidad" (Home) como en "Mis proyectos / Demos" (Perfil).
 */
export default function ProjectCard({ titulo, autor, descripcion, tags, vistas, likes }) {
  return (
    <div className="rounded-xl2 border border-line bg-surface p-4 flex flex-col gap-3">
      <div className="h-24 rounded-lg bg-canvas" />
      <div>
        <p className="font-semibold text-ink text-sm">{titulo}</p>
        {autor && <p className="text-xs text-brand-600">{autor}</p>}
      </div>
      <p className="text-xs text-muted leading-relaxed">{descripcion}</p>
      <div className="flex flex-wrap gap-1.5">
        {tags.map((tag) => (
          <span key={tag} className="text-[11px] bg-canvas text-ink/70 px-2 py-0.5 rounded-full">
            {tag}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between mt-auto pt-1">
        {(vistas != null || likes != null) && (
          <div className="flex items-center gap-3 text-xs text-muted">
            {vistas != null && (
              <span className="flex items-center gap-1">
                <HiOutlineEye /> {vistas}
              </span>
            )}
            {likes != null && (
              <span className="flex items-center gap-1">
                <HiOutlineThumbUp /> {likes}
              </span>
            )}
          </div>
        )}
        <button className="ml-auto text-xs font-semibold border border-line rounded-full px-3 py-1 hover:border-brand-400 hover:text-brand-700 transition-colors">
          Ver Demo
        </button>
      </div>
    </div>
  );
}
