// Usa SettingsPage sem import (para acionar missing import)
export function B() {
  return <div><SettingsPage /></div>;
}

// código com duplicação potencial (mesmo nome em helpers)
export function util() {
  return "dup";
}
