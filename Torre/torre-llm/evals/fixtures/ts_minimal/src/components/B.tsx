// Usa SettingsPage sem import (para acionar missing import)
// eslint-disable-next-line no-undef
export function B() {
  return (
    <div>
      {/* <SettingsPage /> */}
      <div>SettingsPage placeholder</div>
    </div>
  );
}

// código com duplicação potencial (mesmo nome em helpers)
export function util() {
  return "dup";
}
