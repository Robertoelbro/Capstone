import { HiOutlineAcademicCap, HiOutlineFolder, HiOutlineCode, HiOutlineUserGroup } from "react-icons/hi";

const iconos = {
  educacion: HiOutlineAcademicCap,
  proyectos: HiOutlineFolder,
  habilidades: HiOutlineCode,
  conexiones: HiOutlineUserGroup,
};

/** Insignia de cada "rama" del árbol profesional (Educación, Proyectos, etc.) */
export default function RamaBadge({ id, titulo, detalle }) {
  const Icono = iconos[id] ?? HiOutlineFolder;
  return (
    <div className="flex items-center gap-2.5">
      <div className="h-10 w-10 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center text-lg shrink-0">
        <Icono />
      </div>
      <div>
        <p className="text-sm font-semibold text-brand-700">{titulo}</p>
        <p className="text-xs text-muted">{detalle}</p>
      </div>
    </div>
  );
}
