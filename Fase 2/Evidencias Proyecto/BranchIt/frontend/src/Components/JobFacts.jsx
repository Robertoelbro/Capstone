import PropTypes from "prop-types";

export default function JobFacts({ job }) {
  return (
    <dl className="job-facts">
      {job.sueldo != null && (
        <>
          <dt>Sueldo mensual bruto</dt>
          <dd>${Number(job.sueldo).toLocaleString("es-CL")} CLP</dd>
        </>
      )}
      {job.funciones && (
        <>
          <dt>Funciones</dt>
          <dd>{job.funciones}</dd>
        </>
      )}
      {job.perfiles_deseados?.length > 0 && (
        <>
          <dt>Perfiles deseados</dt>
          <dd>{job.perfiles_deseados.join(" · ")}</dd>
        </>
      )}
      {job.condiciones_laborales && (
        <>
          <dt>Condiciones laborales</dt>
          <dd>{job.condiciones_laborales}</dd>
        </>
      )}
      {job.adaptada_discapacidad != null && (
        <>
          <dt>Adaptaciones para personas con discapacidad</dt>
          <dd>{job.adaptada_discapacidad ? "Sí" : "No"}</dd>
        </>
      )}
    </dl>
  );
}
JobFacts.propTypes = { job: PropTypes.object.isRequired };
