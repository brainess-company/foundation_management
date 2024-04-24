# Módulo de Gestão de Fundações

Este módulo foi desenvolvido para gerenciar operações relacionadas a fundações em projetos de construção. Ele ajuda no rastreamento e gerenciamento de maquinário, estacas e medições relacionadas às obras de fundação.

## Funcionalidades

- **Gerenciamento de Obras**: Gerencia obras de construção incluindo detalhes sobre o local, ordens de venda relacionadas e outros aspectos logísticos.
- **Gerenciamento de Maquinário**: Mantém o registro de maquinários envolvidos nos projetos de construção, incluindo operadores e notas específicas relacionadas ao maquinário.
- **Gerenciamento de Estacas**: Administra especificidades sobre as estacas usadas na construção, suas dimensões, profundidade e outras medições.
- **Gerenciamento de Medições**: Rastreia medições relacionadas às fundações, que incluem várias calculações e métricas relacionadas importantes para a integridade estrutural.

## Instalação

Para instalar este módulo, você precisa:

1. Clonar o repositório no diretório de addons do seu Odoo:
   ```bash
   git clone https://github.com/brainess-company/foundation_management.git

## issues
- [ ] Melhorar kanban
- [ ] Baixar medição em pdf para enviar ao cliente
- [x] Enviar medição para conferência de terceiros igual a sale_order
- [x] Inserir assinatura
- [ ] Definir permissões de segurança
- [ ] Uma medição só pode gerar uma unica fatura
- [ ] Da pra fazer um endereço clicado abrir no google maps
- [ ] Opção de gerar medição pelos relatorios
- [ ] Depois que o relatorio for salvo a assinatura fica read only
- [ ] Uma medição só pode ser excluida se nçao tiver uma fatura relacionada
- [ ] Quando uma medição for excluida as estecas tem que ser desrelacionadas com a medição
- [ ] Remover botões de ação desnecessários
- [ ] Lista de presenças (Nao fica salvo nada se nao o operador não preenche, só dá ok e ja era)
- [ ] No cadastro de máquinas a adriana seleciona se a maquina precisa de lista de chamada
- [ ] Quando uma sale order virar uma obra, criar uma account move para cada tipo de item e uma generica
- [ ] Incluir gerenciamento de equipe onde cada funcionario está relacionado a uma equipe (Máquina)
- [ ] E quando for pra ter mais de uma maquina relacionada a um serviço?
- [ ] Pra cada serviço só pode ter uma máquina relacionada mas não é assim que deve funcionar
- [ ] Falta incluir o proprio operador na lista de chamada

