console.log('🏰 Adicionando Torre...');

const torreModels = [
    {id: 'torre-auto', name: '🏰 Torre Auto'},
    {id: 'torre-base', name: '🏰 Torre Base'},
    {id: 'torre-advice', name: '🏰 Torre Advice'},
    {id: 'torre-review', name: '🏰 Torre Review'},
    {id: 'torre-explain', name: '🏰 Torre Explain'}
];

// Função para adicionar as opções de Torre
function adicionarTorreModels() {
    const selects = document.querySelectorAll('select');
    let torresAdicionadas = 0;
    
    selects.forEach(select => {
        // Verifica se o select tem opções e se a primeira contém 'GPT'
        if (select.options.length > 0 && select.options[0].text.includes('GPT')) {
            // Verifica se as Torres já foram adicionadas para evitar duplicação
            const torreJaExiste = Array.from(select.options).some(option => 
                torreModels.some(torre => torre.id === option.value)
            );
            
            if (!torreJaExiste) {
                torreModels.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    select.appendChild(option);
                });
                torresAdicionadas++;
                console.log(`🏰 Torres adicionadas ao select: ${select.name || select.id || 'sem nome'}`);
            }
        }
    });
    
    if (torresAdicionadas > 0) {
        console.log(`🏰 Torre adicionada com sucesso em ${torresAdicionadas} select(s)!`);
    } else {
        console.log('🏰 Nenhum select compatível encontrado ou Torres já existem');
    }
}

// Executa quando o DOM estiver carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', adicionarTorreModels);
} else {
    adicionarTorreModels();
}

// Também executa após um pequeno delay para casos de carregamento dinâmico
setTimeout(adicionarTorreModels, 1000);
