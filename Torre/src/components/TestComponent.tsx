import React from 'react';

// Variável não usada que deve ser prefixada com _
const unusedVar = "test";

// Função com parâmetro não usado
function testFunction(unusedParam: string) {
    return "hello";
}

// Componente que usa SettingsPage sem import
export function TestComponent() {
    return (
        <div>
            <SettingsPage />
            <p>Test component</p>
        </div>
    );
}
