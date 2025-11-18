# 🏰 Como Adicionar Torre aos Modelos do Cursor

## 🎯 **PASSO A PASSO SIMPLES:**

### **1. Abrir Console do Cursor:**

- **Cmd+Option+I** (ou **Ctrl+Shift+I** no Windows)
- Ou **Cmd+Shift+P** → "Developer: Toggle Developer Tools"

### **2. Colar o Script:**

- Copiar todo o conteúdo do arquivo `cursor-torre-integration.js`
- Colar no console do Cursor
- Pressionar **Enter**

### **3. Verificar se Funcionou:**

- Procurar por "🏰 Torre" na lista de modelos
- Deve aparecer:
  - 🏰 Torre Auto
  - 🏰 Torre Base
  - 🏰 Torre Advice
  - 🏰 Torre Review
  - 🏰 Torre Explain

---

## 🚀 **SCRIPT RÁPIDO:**

```javascript
// Copiar e colar isto no console do Cursor:

console.log("🏰 Adicionando Torre...");

const torreModels = [
  { id: "torre-auto", name: "🏰 Torre Auto" },
  { id: "torre-base", name: "🏰 Torre Base" },
  { id: "torre-advice", name: "🏰 Torre Advice" },
  { id: "torre-review", name: "🏰 Torre Review" },
  { id: "torre-explain", name: "🏰 Torre Explain" },
];

document.querySelectorAll("select").forEach((select) => {
  if (select.options.length > 0 && select.options[0].text.includes("GPT")) {
    torreModels.forEach((model) => {
      const option = document.createElement("option");
      option.value = model.id;
      option.textContent = model.name;
      select.appendChild(option);
    });
    console.log("🏰 Torre adicionado!");
  }
});
```

---

## ✅ **RESULTADO:**

**Após executar o script, vais ver:**

- ✅ **🏰 Torre Auto** na lista de modelos
- ✅ **🏰 Torre Base** na lista de modelos
- ✅ **🏰 Torre Advice** na lista de modelos
- ✅ **🏰 Torre Review** na lista de modelos
- ✅ **🏰 Torre Explain** na lista de modelos

**Agora podes selecionar e falar com a Torre!** 🏰✨
