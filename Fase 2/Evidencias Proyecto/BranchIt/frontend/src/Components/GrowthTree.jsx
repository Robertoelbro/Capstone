import PropTypes from "prop-types";

export default function GrowthTree({ percent = 0 }) {
  return (
    <div className="growth-tree">
      <svg
        viewBox="0 0 360 300"
        role="img"
        aria-label={`Tu árbol profesional: ${percent}% del perfil completo`}
      >
        <ellipse cx="180" cy="275" rx="102" ry="12" fill="#d5ddbd" />
        <path
          d="M155 278 Q181 232 170 173 L181 108 L193 173 Q183 234 208 278 Z"
          fill="#806446"
        />
        <g fill="none" stroke="#806446" strokeWidth="10" strokeLinecap="round">
          <path d="M179 229 Q145 208 120 165 M181 202 Q224 191 249 147 M181 181 Q146 155 137 121 M183 158 Q212 135 219 106" />
        </g>
        <g opacity={0.45 + percent / 180}>
          <ellipse
            cx="106"
            cy="147"
            rx="57"
            ry="47"
            fill="#4d713d"
            transform="rotate(-15 106 147)"
          />
          <ellipse
            cx="247"
            cy="140"
            rx="62"
            ry="47"
            fill="#6b8b41"
            transform="rotate(18 247 140)"
          />
          <ellipse cx="155" cy="110" rx="59" ry="61" fill="#769847" />
          <ellipse cx="212" cy="93" rx="58" ry="60" fill="#adc86e" />
          <ellipse
            cx="118"
            cy="101"
            rx="43"
            ry="34"
            fill="#c1d985"
            transform="rotate(-28 118 101)"
          />
          <ellipse cx="189" cy="151" rx="62" ry="43" fill="#45623b" />
          <ellipse cx="254" cy="109" rx="35" ry="29" fill="#d0dfa1" />
          <path
            d="M103 167 Q150 141 171 107 M214 52 Q194 118 187 158 M239 164 Q211 150 197 138"
            stroke="#edf2c8"
            strokeWidth="2"
            fill="none"
            opacity=".6"
          />
        </g>
        <path
          d="M134 278 Q121 256 105 266 Q113 277 134 278 M217 279 Q239 251 253 267 Q243 280 217 279"
          fill="#84a250"
        />
        <circle
          cx="181"
          cy="253"
          r="31"
          fill="#fcfbf5"
          stroke="#729347"
          strokeWidth="3"
        />
        <text
          x="181"
          y="260"
          textAnchor="middle"
          fill="#29442f"
          fontSize="22"
          fontFamily="Georgia,serif"
        >
          {percent}%
        </text>
        <g fill="#bb7e4a">
          <circle cx="79" cy="209" r="4" />
          <circle cx="280" cy="69" r="3" />
          <circle cx="285" cy="214" r="4" />
        </g>
      </svg>
    </div>
  );
}
GrowthTree.propTypes = { percent: PropTypes.number };
