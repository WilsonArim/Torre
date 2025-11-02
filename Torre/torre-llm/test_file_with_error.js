// Arquivo de teste com erros para demonstrar a Torre
// Este arquivo tinha vários erros que foram corrigidos automaticamente

function testFunction() {
    console.log("Hello World");
    
    const array = [1, 2, 3, 4, 5];
    
    let result = array.map(x => x * 2);
    
    return result;
}

// Variável não declarada (mantida para demonstrar erro de runtime, não de sintaxe)
// console.log(undefinedVariable);

// Função chamada corretamente
testFunction();

// String fechada corretamente
const message = "Esta string está fechada";

// Objeto bem formado
const obj = {
    name: "test",
    value: 123,
    active: true
};

// Array bem formado
const arr = [1, 2, 3, 4];

// Função com sintaxe correta
function anotherTest() {
    if (true) {
        console.log("Sintaxe correta");
    }
}

// Export bem formado
module.exports = testFunction;
