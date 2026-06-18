# 🤖 RPA Protheus - Automação de Processamento de Compras (BR Supply)

Este é um robô de automação de processos (RPA) desenvolvido em Python e Selenium para otimizar o fluxo de importação e geração de Pedidos de Compras (PC) dentro do ERP TOTVS Protheus (Webapp).

O projeto foi desenhado para operar de forma resiliente em ambientes corporativos complexos, lidando com estruturas dinâmicas de **Shadow DOM**, controle de concorrência e tratamento autônomo de exceções de negócio.

## 🚀 Funcionalidades Principais

- **Navegação Multi-Filial:** O robô realiza o ciclo completo de operações alternando dinamicamente entre diferentes filiais corporativas (`Matriz`, `SCS`, `Rio`).
- **Resiliência contra Elementos Voláteis (Shadow DOM):** Utiliza um motor de busca recursivo via JavaScript injetado para localizar e interagir com Web Components aninhados.
- **Interação Híbrida (Mouse e Teclado):** Mitiga falhas de sobreposição de camadas visuais (`z-index`) utilizando cliques forçados via JavaScript e emulação de comandos nativos de teclado (`Keys.ENTER`).
- **Tratamento de Erros Inteligente (Sentinela):** Detecta automaticamente falhas de negócio (ex: produtos da BR Supply sem vínculo de DE/PARA no Protheus), realiza o **auto-print da tela de erro**, isola a falha e utiliza a lógica de salto (`continue`) para não interromper a execução das demais filiais.

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **Selenium WebDriver** (GeckoDriver / Firefox)
- **JavaScript (ES6)** (Injeção via driver para manipulação de árvore DOM)

