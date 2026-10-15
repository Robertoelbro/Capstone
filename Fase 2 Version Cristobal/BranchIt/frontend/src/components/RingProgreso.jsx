/**
 * Anillo de progreso circular (CSS conic-gradient), reutilizado para
 * "Compatibilidad general" en Home y "Crecimiento general" en Perfil.
 */
export default function RingProgreso({ porcentaje, size = 72, grosor = 7, children }) {
  const estiloAnillo = {
    width: size,
    height: size,
    background: `conic-gradient(#3B703D ${porcentaje * 3.6}deg, #E7E7F0 0deg)`,
  };
  const estiloHueco = {
    inset: grosor,
  };

  return (
    <div className="relative rounded-full shrink-0" style={estiloAnillo}>
      <div className="absolute rounded-full bg-surface flex items-center justify-center" style={estiloHueco}>
        {children ?? (
          <span className="text-sm font-bold text-brand-700">{porcentaje}%</span>
        )}
      </div>
    </div>
  );
}
