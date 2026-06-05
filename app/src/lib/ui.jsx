/* Shared primitives: Pill (status/layer), Btn, statusKind. */
import { Icon } from "./icons.jsx";

export function Pill({ kind, children }) {
  return <span className={"pill " + kind}><span className="pdot" />{children || kind}</span>;
}

export function Btn({ variant = "secondary", icon, children, ...rest }) {
  return (
    <button className={"btn btn-" + variant} {...rest}>
      {icon && <Icon name={icon} size={15} />}
      {children}
    </button>
  );
}

/* status → pill kind */
export function statusKind(s) {
  return s === "confirmed" ? "confirmed"
    : s === "in-progress" ? "in-progress"
    : s === "draft" ? "draft" : "draft";
}
