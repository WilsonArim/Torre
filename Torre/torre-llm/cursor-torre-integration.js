// Script para injetar modelos da Torre no Cursor
// Execute isto no console do Cursor (Cmd+Option+I)

console.log('🏰 Injetando modelos da Torre no Cursor...');

// Função para adicionar modelos da Torre
function addTorreModels() {
    try {
        // Verificar se já existe
        if (window.torreModelsAdded) {
            console.log('🏰 Modelos da Torre já foram adicionados');
            return;
        }

        // Simular modelos da Torre
        const torreModels = [
            {
                id: 'torre-auto',
                name: '🏰 Torre Auto',
                description: 'Correção automática inteligente',
                provider: 'torre',
                contextLength: 100000,
                supportsCodeActions: true
            },
            {
                id: 'torre-base',
                name: '🏰 Torre Base',
                description: 'Correções básicas e sintaxe',
                provider: 'torre',
                contextLength: 50000,
                supportsCodeActions: true
            },
            {
                id: 'torre-advice',
                name: '🏰 Torre Advice',
                description: 'Sugestões e boas práticas',
                provider: 'torre',
                contextLength: 75000,
                supportsCodeActions: true
            },
            {
                id: 'torre-review',
                name: '🏰 Torre Review',
                description: 'Code review e segurança',
                provider: 'torre',
                contextLength: 60000,
                supportsCodeActions: true
            },
            {
                id: 'torre-explain',
                name: '🏰 Torre Explain',
                description: 'Explicação e documentação',
                provider: 'torre',
                contextLength: 80000,
                supportsCodeActions: true
            }
        ];

        // Tentar encontrar o seletor de modelos
        const modelSelectors = [
            '[data-testid="model-selector"]',
            '.model-selector',
            '[aria-label*="model"]',
            'select[aria-label*="model"]',
            '.cursor-model-selector'
        ];

        let modelSelector = null;
        for (const selector of modelSelectors) {
            const element = document.querySelector(selector);
            if (element) {
                modelSelector = element;
                break;
            }
        }

        if (modelSelector) {
            console.log('🏰 Seletor de modelos encontrado:', modelSelector);
            
            // Adicionar opções da Torre
            torreModels.forEach(model => {
                const option = document.createElement('option');
                option.value = model.id;
                option.textContent = model.name;
                option.setAttribute('data-description', model.description);
                modelSelector.appendChild(option);
            });

            console.log('🏰 Modelos da Torre adicionados com sucesso!');
        } else {
            console.log('🏰 Seletor de modelos não encontrado, tentando método alternativo...');
            
            // Método alternativo: procurar por elementos que parecem ser seletor de modelos
            const allSelects = document.querySelectorAll('select');
            allSelects.forEach(select => {
                if (select.options.length > 0 && 
                    (select.options[0].text.includes('GPT') || 
                     select.options[0].text.includes('Claude') ||
                     select.options[0].text.includes('Gemini'))) {
                    
                    console.log('🏰 Seletor de modelos encontrado (método alternativo):', select);
                    
                    // Adicionar opções da Torre
                    torreModels.forEach(model => {
                        const option = document.createElement('option');
                        option.value = model.id;
                        option.textContent = model.name;
                        option.setAttribute('data-description', model.description);
                        select.appendChild(option);
                    });
                }
            });
        }

        // Marcar como adicionado
        window.torreModelsAdded = true;
        
        // Mostrar notificação
        if (window.showInformationMessage) {
            window.showInformationMessage('🏰 Modelos da Torre adicionados!');
        } else {
            console.log('🏰 Modelos da Torre adicionados! Agora podes selecioná-los.');
        }

    } catch (error) {
        console.error('🏰 Erro ao adicionar modelos da Torre:', error);
    }
}

// Executar imediatamente
addTorreModels();

// Executar novamente após um delay (caso o DOM ainda não esteja pronto)
setTimeout(addTorreModels, 1000);
setTimeout(addTorreModels, 3000);

console.log('🏰 Script de injeção da Torre executado!');
console.log('🏰 Procura por "🏰 Torre" na lista de modelos do Cursor!');
