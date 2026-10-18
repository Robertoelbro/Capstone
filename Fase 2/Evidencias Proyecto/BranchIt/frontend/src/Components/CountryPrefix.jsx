import { useEffect, useId, useRef, useState } from "react";
import PropTypes from "prop-types";
import { searchKey } from "../data/catalogs";

const flags = import.meta.glob(
  "../../node_modules/country-flag-icons/3x2/*.svg",
  { eager: true, as: "url" },
);
const flag = (code) =>
  flags[`../../node_modules/country-flag-icons/3x2/${code}.svg`];

export default function CountryPrefix({ value, options, onChange }) {
  const id = useId();
  const root = useRef(null),
    button = useRef(null),
    search = useRef(null);
  const [open, setOpen] = useState(false),
    [query, setQuery] = useState(""),
    [active, setActive] = useState(0);
  const selected = options.find((item) => item.value === value);
  const matches = options.filter((item) =>
    searchKey(`${item.name} ${item.prefix}`).includes(searchKey(query)),
  );
  useEffect(() => {
    const close = (e) => {
      if (!root.current?.contains(e.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);
  useEffect(() => {
    if (open) search.current?.focus();
  }, [open]);
  useEffect(() => {
    if (open)
      document
        .getElementById(`${id}-${active}`)
        ?.scrollIntoView({ block: "nearest" });
  }, [open, active, id]);
  function choose(item) {
    onChange(item.value);
    setOpen(false);
    button.current?.focus();
  }
  return (
    <div
      className="country-prefix"
      ref={root}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) setOpen(false);
      }}
    >
      <button
        ref={button}
        type="button"
        className="country-trigger"
        aria-label={`País y prefijo telefónico: ${selected.name} ${selected.prefix}`}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? `${id}-list` : undefined}
        onClick={() => {
          setOpen(!open);
          setQuery("");
          setActive(0);
        }}
        onKeyDown={(e) => {
          if (["ArrowDown", "ArrowUp"].includes(e.key)) {
            e.preventDefault();
            setOpen(true);
          }
        }}
      >
        <img src={flag(selected.code)} alt="" width="26" height="18" />
        <span>{selected.prefix}</span>
        <span aria-hidden="true">⌄</span>
      </button>
      {open && (
        <div className="country-dropdown">
          <input
            ref={search}
            role="combobox"
            aria-label="Buscar país"
            placeholder="Buscar país"
            aria-expanded="true"
            aria-controls={`${id}-list`}
            aria-autocomplete="list"
            aria-activedescendant={
              matches.length ? `${id}-${active}` : undefined
            }
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
            onKeyDown={(e) => {
              if (e.key === "Escape") {
                setOpen(false);
                button.current?.focus();
              }
              if (["ArrowDown", "ArrowUp"].includes(e.key)) {
                e.preventDefault();
                setActive((n) =>
                  Math.max(
                    0,
                    Math.min(
                      matches.length - 1,
                      n + (e.key === "ArrowDown" ? 1 : -1),
                    ),
                  ),
                );
              }
              if (e.key === "Enter") {
                e.preventDefault();
                if (matches[active]) choose(matches[active]);
              }
            }}
          />
          <ul
            id={`${id}-list`}
            role="listbox"
            aria-label="País y prefijo telefónico"
          >
            {matches.map((item, i) => (
              <li
                role="option"
                id={`${id}-${i}`}
                key={item.value}
                aria-label={`${item.name} ${item.prefix}`}
                aria-selected={item.value === value}
                className={i === active ? "country-active" : ""}
                title={item.name}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => choose(item)}
              >
                <img src={flag(item.code)} alt="" width="26" height="18" />
                <span>{item.prefix}</span>
              </li>
            ))}
          </ul>
          {!matches.length && <p>Sin resultados.</p>}
        </div>
      )}
    </div>
  );
}
CountryPrefix.propTypes = {
  value: PropTypes.string.isRequired,
  options: PropTypes.array.isRequired,
  onChange: PropTypes.func.isRequired,
};
