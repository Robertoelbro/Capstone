import { HiOutlineUserCircle, HiOutlinePlus } from "react-icons/hi";
import RingProgreso from "../components/RingProgreso";
import ArbolIlustracion from "../components/ArbolIlustracion";
import RamaBadge from "../components/RamaBadge";
import ProjectCard from "../components/ProjectCard";
import {
  usuarioActual,
  ramasArbol,
  habilidades,
  estadisticas,
  guardadosTotal,
  misProyectos,
} from "../data/mockData";

export default function Profile() {
  const [educacion, proyectos, habilidadesRama, conexiones] = ramasArbol;

  return (
    <div className="flex flex-col gap-6">
      {/* Tarjeta de usuario */}
      <section className="rounded-xl2 border border-line bg-surface p-5 flex flex-wrap items-center gap-5">
        <div className="h-16 w-16 rounded-full bg-canvas text-muted flex items-center justify-center text-4xl shrink-0">
          <HiOutlineUserCircle />
        </div>
        <div className="flex-1 min-w-[220px]">
          <p className="font-bold text-ink">{usuarioActual.nombre}</p>
          <p className="text-sm text-muted">{usuarioActual.titulo}</p>
          <p className="text-xs text-muted">{usuarioActual.ubicacion}</p>
          <p className="text-sm text-ink/80 mt-2 max-w-xl">{usuarioActual.bio}</p>
        </div>
        <button className="text-sm font-semibold border border-line rounded-full px-4 py-2 hover:border-brand-400 hover:text-brand-700 transition-colors shrink-0">
          Editar perfil
        </button>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_300px] items-start">
        {/* Árbol profesional */}
        <section className="rounded-xl2 border border-line bg-surface p-5 lg:p-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-semibold text-ink">Mi árbol profesional</h2>
            <button className="text-xs font-semibold border border-line rounded-full px-3 py-1.5 hover:border-brand-400 hover:text-brand-700 transition-colors">
              Ver árbol completo
            </button>
          </div>

          <div className="grid grid-cols-2 gap-x-6 gap-y-8 items-center max-w-xl mx-auto">
            <RamaBadge {...educacion} />
            <div className="justify-self-end text-right">
              <RamaBadge {...proyectos} />
            </div>

            <div className="col-span-2 flex flex-col items-center -my-2">
              <ArbolIlustracion className="w-36 h-32" />
              <RingProgreso porcentaje={usuarioActual.crecimiento} size={64}>
                <span className="text-xs font-bold text-brand-700">{usuarioActual.crecimiento}%</span>
              </RingProgreso>
              <span className="text-[11px] text-muted mt-1">Crecimiento general</span>
            </div>

            <RamaBadge {...habilidadesRama} />
            <div className="justify-self-end text-right">
              <RamaBadge {...conexiones} />
            </div>
          </div>
        </section>

        {/* Columna derecha: habilidades + estadísticas */}
        <div className="flex flex-col gap-6">
          <section className="rounded-xl2 border border-line bg-surface p-4">
            <h2 className="text-sm font-semibold text-ink mb-3">Mis habilidades</h2>
            <ul className="flex flex-col gap-3">
              {habilidades.map((h) => (
                <li key={h.id}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-ink">{h.nombre}</span>
                    <span className="text-muted">{h.etiqueta}</span>
                  </div>
                  <div className="progreso-pista h-2 w-full">
                    <div className="progreso-relleno h-full" style={{ width: `${h.nivel}%` }} />
                  </div>
                </li>
              ))}
            </ul>
            <button className="text-xs font-semibold text-brand-600 hover:text-brand-700 mt-3">
              Ver Todas
            </button>
          </section>

          <section className="rounded-xl2 border border-line bg-surface p-4">
            <h2 className="text-sm font-semibold text-ink mb-3">Mis estadísticas</h2>
            <div className="grid grid-cols-3 gap-3 text-center">
              {estadisticas.map((e) => (
                <div key={e.id}>
                  <p className="text-xl font-bold text-ink">{e.valor}</p>
                  <p className="text-[11px] text-muted">{e.etiqueta}</p>
                </div>
              ))}
            </div>
            <div className="text-center mt-4 pt-4 border-t border-line">
              <p className="text-xl font-bold text-ink">{guardadosTotal}</p>
              <p className="text-[11px] text-muted">Guardados</p>
            </div>
          </section>
        </div>
      </div>

      {/* Mis proyectos / Demos */}
      <section>
        <h2 className="font-semibold text-ink mb-3">Mis proyectos / Demos</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {misProyectos.map((p) => (
            <ProjectCard
              key={p.id}
              titulo={p.titulo}
              descripcion={p.descripcion}
              tags={p.tags}
            />
          ))}
          <button className="rounded-xl2 border-2 border-dashed border-line text-muted hover:border-brand-400 hover:text-brand-700 transition-colors flex flex-col items-center justify-center gap-2 min-h-[160px]">
            <HiOutlinePlus className="text-2xl" />
            <span className="text-sm font-medium">Agregar proyecto</span>
            <span className="text-xs">Sube un nuevo proyecto y muestra tu talento</span>
          </button>
        </div>
      </section>
    </div>
  );
}
