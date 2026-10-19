import CountryPrefix from "./CountryPrefix";
import { useEffect, useId, useRef, useState } from "react";
import PropTypes from "prop-types";
import {
  getCountries,
  getCountryCallingCode,
  AsYouType,
  parsePhoneNumberFromString,
} from "libphonenumber-js";
import { searchKey } from "../data/catalogs";
import "./FormFields.css";

export function ValidatedForm({ children, ...props }) {
  const [attempted, setAttempted] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    // Add a visible and accessible required marker to both wrapped and linked labels.
    const mark = () => {
      ref.current
        ?.querySelectorAll("label .required-mark")
        .forEach((marker) => {
          if (!marker.closest("label")?.control?.required) marker.remove();
        });
      ref.current
        ?.querySelectorAll(
          "input[required],textarea[required],select[required]",
        )
        .forEach((input) => {
          for (const label of input.labels || []) {
            if (!label.querySelector(".required-mark")) {
              const marker = document.createElement("span");
              marker.className = "required-mark";
              marker.textContent = " *";
              marker.setAttribute("aria-hidden", "true");
              const text = [...label.childNodes].find(
                (node) =>
                  node.nodeType === Node.TEXT_NODE && node.textContent.trim(),
              );
              if (text) text.after(marker);
              else label.prepend(marker);
            }
          }
        });
    };
    mark();
    const observer = new MutationObserver(mark);
    observer.observe(ref.current, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["required"],
    });
    return () => observer.disconnect();
  }, []);
  return (
    <form
      {...props}
      ref={ref}
      data-validated={attempted}
      onInvalidCapture={(e) => {
        setAttempted(true);
        e.target.setAttribute("aria-invalid", "true");
      }}
      onInputCapture={(e) => {
        if (e.target.validity?.valid) e.target.removeAttribute("aria-invalid");
      }}
    >
      {attempted && (
        <p className="validation-hint" role="status">
          Los campos obligatorios se indican con *.
        </p>
      )}
      {children}
    </form>
  );
}
ValidatedForm.propTypes = { children: PropTypes.node };

export function SearchField({
  label,
  name,
  options,
  value = "",
  onChange,
  required = false,
}) {
  const id = useId();
  const [query, setQuery] = useState(value || "");
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);
  const box = useRef(null);
  const input = useRef(null);
  const [selected, setSelected] = useState(value || "");
  const [other, setOther] = useState(
    Boolean(value && !options.includes(value)),
  );
  useEffect(() => {
    if (value) {
      setSelected(value);
      setQuery(value);
      setOther(!options.includes(value));
    }
  }, [value, options]);
  useEffect(() => {
    const close = (e) => {
      if (!box.current?.contains(e.target)) setOpen(false);
    };
    document.addEventListener("pointerdown", close);
    return () => document.removeEventListener("pointerdown", close);
  }, []);
  const matches = options.filter((option) =>
    searchKey(option).includes(searchKey(query)),
  );
  const choices = [...matches, "Otros"];
  useEffect(() => {
    if (open)
      document
        .getElementById(`${id}-option-${active}`)
        ?.scrollIntoView({ block: "nearest" });
  }, [open, active, id]);
  function choose(option) {
    setOpen(false);
    setActive(0);
    if (option === "Otros") {
      setOther(true);
      setQuery("");
      setSelected("");
      onChange?.("");
    } else {
      setOther(false);
      setQuery(option);
      setSelected(option);
      onChange?.(option);
    }
    input.current?.focus();
  }
  useEffect(() => {
    const message =
      query && !selected && !other
        ? "Selecciona una opción de la lista o elige Otros."
        : "";
    input.current?.setCustomValidity(message);
    if (!message) input.current?.removeAttribute("aria-invalid");
  }, [query, selected, other]);
  return (
    <div
      className="search-field editor-field"
      ref={box}
      onBlur={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget)) setOpen(false);
      }}
    >
      <label htmlFor={id}>{label}</label>
      <input
        ref={input}
        id={id}
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={open ? `${id}-list` : undefined}
        aria-activedescendant={open ? `${id}-option-${active}` : undefined}
        autoComplete="off"
        required={required}
        maxLength={150}
        placeholder={other ? "Especifica otra opción" : "Buscar o seleccionar"}
        value={query}
        onFocus={() => {
          if (!other) setOpen(true);
        }}
        onChange={(e) => {
          const next = e.target.value;
          setQuery(next);
          setActive(0);
          setSelected(other ? next : "");
          onChange?.(other ? next : "");
          setOpen(!other);
        }}
        onKeyDown={(e) => {
          if (e.key === "Escape") setOpen(false);
          if (e.key === "ArrowDown" || e.key === "ArrowUp") {
            e.preventDefault();
            setOpen(true);
            setActive((n) =>
              !open
                ? 0
                : Math.max(
                    0,
                    Math.min(
                      choices.length - 1,
                      n + (e.key === "ArrowDown" ? 1 : -1),
                    ),
                  ),
            );
          }
          if (e.key === "Enter" && open) {
            e.preventDefault();
            choose(choices[active] || "Otros");
          }
        }}
      />
      <input type="hidden" name={name} value={selected} />
      {other && (
        <button
          type="button"
          className="catalog-reset"
          onClick={() => {
            setOther(false);
            setQuery("");
            setSelected("");
            onChange?.("");
            setOpen(true);
            input.current?.focus();
          }}
        >
          Volver al listado
        </button>
      )}
      {open && (
        <ul
          id={`${id}-list`}
          role="listbox"
          aria-label={label}
          className="catalog-options"
        >
          {choices.map((option, i) => (
            <li
              id={`${id}-option-${i}`}
              key={option}
              role="option"
              aria-selected={i === active}
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => choose(option)}
            >
              {option}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
SearchField.propTypes = {
  label: PropTypes.string.isRequired,
  name: PropTypes.string,
  options: PropTypes.array.isRequired,
  value: PropTypes.string,
  onChange: PropTypes.func,
  required: PropTypes.bool,
};

export function RutField({ label = "RUT", name = "rut", required = true }) {
  const [value, setValue] = useState("");
  return (
    <label className="editor-field">
      {label}
      <input
        name={name}
        required={required}
        value={value}
        autoComplete="off"
        maxLength={12}
        placeholder="12.345.678-5"
        onChange={(e) => {
          const raw = e.target.value
            .replace(/[^0-9kK]/g, "")
            .slice(0, 9)
            .toUpperCase();
          const body = raw.slice(0, -1).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
          setValue(raw.length > 1 ? `${body}-${raw.slice(-1)}` : raw);
        }}
      />
    </label>
  );
}
RutField.propTypes = {
  label: PropTypes.string,
  name: PropTypes.string,
  required: PropTypes.bool,
};

export function MoneyField({ value, onChange }) {
  return (
    <label className="editor-field">
      Sueldo mensual bruto (CLP)
      <input
        required
        type="text"
        inputMode="numeric"
        pattern="[1-9][0-9.]*"
        maxLength={14}
        value={value ? Number(value).toLocaleString("es-CL") : ""}
        placeholder="850.000"
        onChange={(e) =>
          onChange(e.target.value.replace(/\D/g, "").slice(0, 10))
        }
      />
    </label>
  );
}
MoneyField.propTypes = {
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  onChange: PropTypes.func.isRequired,
};

const names = new Intl.DisplayNames(["es"], { type: "region" });
const countries = getCountries()
  .map((code) => ({
    code,
    label: `${names.of(code)} (+${getCountryCallingCode(code)})`,
  }))
  .sort((a, b) => a.label.localeCompare(b.label, "es"));
const phoneOptions = [
  { value: "CL-mobile", code: "CL", name: "Chile móvil", prefix: "+569" },
  ...countries.map((item) => ({
    value: item.code,
    code: item.code,
    name: names.of(item.code),
    prefix: `+${getCountryCallingCode(item.code)}`,
  })),
];
function splitPhone(value) {
  const parsed = parsePhoneNumberFromString(value || "");
  if (parsed?.country === "CL" && parsed.nationalNumber.startsWith("9"))
    return { country: "CL-mobile", number: parsed.nationalNumber.slice(1) };
  return {
    country: parsed?.country || "CL-mobile",
    number: parsed?.nationalNumber || "",
  };
}
export function PhoneField({
  label = "Teléfono",
  name = "telefono",
  value,
  onChange,
  required = false,
}) {
  const id = useId();
  const initial = splitPhone(value);
  const [country, setCountry] = useState(initial.country);
  const [number, setNumber] = useState(initial.number);
  const mobile = country === "CL-mobile";
  const code = mobile ? "CL" : country;
  const prefix = mobile ? "+569" : `+${getCountryCallingCode(code)}`;
  const combined = number ? prefix + number : "";
  const ref = useRef(null);
  useEffect(() => {
    const parsed = combined ? parsePhoneNumberFromString(combined) : null;
    const message =
      combined && (!parsed?.isPossible() || (mobile && number.length !== 8))
        ? "Revisa la cantidad de dígitos del teléfono."
        : "";
    ref.current?.setCustomValidity(message);
    if (!message) ref.current?.removeAttribute("aria-invalid");
  }, [combined, mobile, number]);
  function change(nextCountry, nextNumber) {
    setCountry(nextCountry);
    setNumber(nextNumber);
    const pre =
      nextCountry === "CL-mobile"
        ? "+569"
        : `+${getCountryCallingCode(nextCountry)}`;
    onChange?.(nextNumber ? pre + nextNumber : "");
  }
  const display = mobile
    ? number.replace(/(\d{4})(?=\d)/g, "$1 ")
    : new AsYouType(code).input(number);
  return (
    <div className="editor-field">
      <label htmlFor={id}>{label}</label>
      <div className="phone-fields">
        <CountryPrefix
          value={country}
          options={phoneOptions}
          onChange={(next) => change(next, number)}
        />
        <input
          ref={ref}
          id={id}
          type="tel"
          inputMode="tel"
          autoComplete="tel-national"
          required={required}
          value={display}
          placeholder={mobile ? "1234 5678" : "Número"}
          onChange={(e) => {
            let digits = e.target.value.replace(/\D/g, "");
            if (
              e.target.value.trim().startsWith("+") &&
              digits.startsWith(prefix.slice(1))
            )
              digits = digits.slice(prefix.length - 1);
            else if (mobile && digits.length === 9 && digits.startsWith("9"))
              digits = digits.slice(1);
            change(
              country,
              digits.slice(0, mobile ? 8 : 15 - prefix.length + 1),
            );
          }}
        />
      </div>
      <input type="hidden" name={name} value={combined} />
    </div>
  );
}
PhoneField.propTypes = {
  label: PropTypes.string,
  name: PropTypes.string,
  value: PropTypes.string,
  onChange: PropTypes.func,
  required: PropTypes.bool,
};
