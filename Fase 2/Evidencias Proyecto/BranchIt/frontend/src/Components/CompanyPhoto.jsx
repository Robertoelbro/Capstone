import PropTypes from 'prop-types';
import { Asset } from './Media';

export default function CompanyPhoto({ job }) {
  return <span className="company-photo">
    {job.empresa_foto_id ? <Asset id={job.empresa_foto_id} alt={`Foto de ${job.nombre_empresa}`} />
      : job.empresa_logo_url ? <img src={job.empresa_logo_url} alt={`Logo de ${job.nombre_empresa}`} loading="lazy" />
      : <span aria-label={job.nombre_empresa}>{job.nombre_empresa?.replace('DEMO · ', '').slice(0, 2).toUpperCase()}</span>}
  </span>;
}
CompanyPhoto.propTypes = { job: PropTypes.object.isRequired };
