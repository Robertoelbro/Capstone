<<<<<<< Updated upstream
import { Link } from "react-router-dom";
import "./Home.css";

export default function Home() {
  return (
    <div className="contenedor home">
      <section className="home-hero">
        <svg
          className="home-hero__rama"
          viewBox="0 0 200 200"
          role="presentation"
          aria-hidden="true"
        >
          <path
            d="M100 190 V110 M100 110 C60 110 60 70 40 40 M100 110 C140 110 140 70 160 40 M100 150 C70 150 70 120 55 100 M100 150 C130 150 130 120 145 100"
            fill="none"
            stroke="var(--color-primary)"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx="40" cy="40" r="6" fill="var(--color-accent)" />
          <circle cx="160" cy="40" r="6" fill="var(--color-accent)" />
          <circle cx="55" cy="100" r="5" fill="var(--color-primary-light)" />
          <circle cx="145" cy="100" r="5" fill="var(--color-primary-light)" />
        </svg>

        <div>
          <h1>Cada egresado tiene varios caminos por delante.</h1>
          <p className="home-hero__bajada">
            BranchIt conecta a egresados de DuocUC con empresas que publican
            ofertas de empleo reales, en un solo lugar.
          </p>
          <div className="home-hero__acciones">
            <Link to="/registro/egresado" className="boton boton-primario">
              Soy egresado
            </Link>
            <Link to="/registro/empresa" className="boton boton-secundario">
              Soy empresa
            </Link>
          </div>
        </div>
      </section>
=======
import { PiRobotBold } from "react-icons/pi";
import RingProgreso from "../components/RingProgreso";
import ProjectCard from "../components/ProjectCard";
import {
  recomendacionesIA,
  compatibilidadIA,
  proyectosComunidad,
  tipsCrecimiento,
  actividadReciente,
  ofertasRecomendadas,
} from "../data/mockData";

export default function Home() {
  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_320px] items-start">
      {/* Columna principal */}
      <div className="flex flex-col gap-8 min-w-0">
        <div>
          <h1 className="text-xl font-bold text-ink">Para ti</h1>
          <p className="text-sm text-muted">
            Oportunidades y contenido seleccionado según tu perfil
          </p>
        </div>

        {/* Tarjeta BranchIt IA */}
        <section className="rounded-xl2 border border-brand-200 bg-brand-50/60 p-5">
          <div className="flex flex-wrap items-start gap-4">
            <div className="flex items-center gap-3 shrink-0">
              <div className="h-12 w-12 rounded-full bg-surface flex items-center justify-center text-2xl text-brand-600 shadow-card">
                <PiRobotBold />
              </div>
              <div>
                <p className="font-bold text-ink">BranchIt IA</p>
                <p className="text-xs text-muted max-w-[16rem]">
                  Encontramos oportunidades para ti analizando tu perfil, habilidades y proyectos.
                </p>
              </div>
            </div>

            <div className="flex flex-col items-center gap-1 mx-auto sm:mx-0">
              <RingProgreso porcentaje={compatibilidadIA} />
              <span className="text-[11px] text-muted text-center">Compatibilidad general</span>
            </div>

            <div className="flex-1 min-w-[220px] bg-surface rounded-xl border border-line p-3 flex flex-col gap-2">
              {recomendacionesIA.map((r) => (
                <div key={r.id} className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-full bg-canvas shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-ink truncate">{r.cargo}</p>
                    <p className="text-xs text-muted truncate">{r.empresa}</p>
                  </div>
                </div>
              ))}
              <button className="mt-1 self-start text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-full px-3 py-1.5 transition-colors">
                Ver recomendaciones
              </button>
            </div>
          </div>
        </section>

        {/* Proyectos destacados de la comunidad */}
        <section>
          <h2 className="font-semibold text-ink mb-3">Proyecto destacados de la comunidad</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {proyectosComunidad.map((p) => (
              <ProjectCard
                key={p.id}
                titulo={p.titulo}
                autor={p.autor}
                descripcion={p.descripcion}
                tags={p.tags}
                vistas={p.vistas}
                likes={p.likes}
              />
            ))}
          </div>
        </section>

        {/* Sigue aprendiendo y creciendo */}
        <section>
          <h2 className="font-semibold text-ink mb-3">Sigue aprendiendo y creciendo 🌱</h2>
          <div className="grid sm:grid-cols-3 gap-4">
            {tipsCrecimiento.map((tip) => (
              <div
                key={tip.id}
                className="rounded-xl2 border border-line bg-surface p-4 flex items-center gap-3"
              >
                <div className="h-9 w-9 rounded-full bg-brand-100 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-ink">{tip.titulo}</p>
                  <p className="text-xs text-brand-600">{tip.detalle}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Columna derecha */}
      <div className="flex flex-col gap-6">
        <section className="rounded-xl2 border border-line bg-surface p-4">
          <h2 className="text-sm font-semibold text-brand-700 mb-3">Actividad reciente</h2>
          <ul className="flex flex-col gap-3">
            {actividadReciente.map((a) => (
              <li key={a.id} className="flex items-start gap-3">
                <div className="h-8 w-8 rounded-md bg-canvas shrink-0 mt-0.5" />
                <div className="min-w-0">
                  <p className="text-sm text-ink truncate">{a.titulo}</p>
                  <p className="text-xs text-muted truncate">{a.detalle}</p>
                  <p className="text-[11px] text-muted/80">{a.cuando}</p>
                </div>
              </li>
            ))}
          </ul>
          <button className="text-xs font-semibold text-brand-600 hover:text-brand-700 mt-3">
            Ver toda la actividad
          </button>
        </section>

        <section className="rounded-xl2 border border-line bg-surface p-4">
          <h2 className="text-sm font-semibold text-ink mb-3">Ofertas recomendadas para ti</h2>
          <ul className="flex flex-col gap-4">
            {ofertasRecomendadas.map((o) => (
              <li key={o.id} className="flex items-start gap-3">
                <div
                  className={`h-9 w-9 rounded-full ${o.color} text-white text-sm font-bold flex items-center justify-center shrink-0`}
                >
                  {o.inicial}
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-ink leading-tight">{o.cargo}</p>
                  <p className="text-xs text-muted">
                    {o.empresa} · {o.ubicacion}
                  </p>
                  <span className="text-[11px] text-brand-600 font-medium">{o.modalidad}</span>
                </div>
              </li>
            ))}
          </ul>
          <button className="text-xs font-semibold text-brand-600 hover:text-brand-700 mt-3">
            Ver más ofertas
          </button>
        </section>
      </div>
>>>>>>> Stashed changes
    </div>
  );
}
