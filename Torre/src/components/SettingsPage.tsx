// @torre: shim para garantir que `base` existe em runtime (Vite/Tauri)
// Evita "ReferenceError: base is not defined".
const base: string =
  ((globalThis as any).__TORRE_BASE__ as string) ??
  (((import.meta as any)?.env?.BASE_URL as string) ?? '/');
(globalThis as any).__TORRE_BASE__ = base;

import React from 'react';

export function SettingsPage() {
    // Uso de base sem shim - vai gerar ReferenceError
    const apiUrl = base + '/api/settings';
    
    return (
        <div>
            <h1>Settings</h1>
            <p>API URL: {apiUrl}</p>
        </div>
    );
}
