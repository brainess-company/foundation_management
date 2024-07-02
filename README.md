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

- **Futuramente**:
- [ ] Baixar medição em pdf para enviar ao cliente
- [ ] Configurar profundidade minima e máxima
- [ ] incluir botão no kanbam para deixar a transferencia pronta
- [ ] Métrica chamada unidades de trabalho, e trabalhadores distintos no período, verificar correlações
- [ ] Estudar o relacionamento com o portal do cliente
- [ ] No portal do cliente aparece todos os projetos relacionados com o cliente se o modulo de fundações criar um projeto o cliente pode acompanhar
- [ ] Criar campo de calculo relativo no produto (area da base de um diametro da estaca) esse valor será multiplicado pela quantidade executada


- **Urgente**:

- [x] Uma estaca só pode ser medida se o relatorio relacionado estiver no estágio confirmado
- [x] Uma medição só pode gerar uma unica fatura
- [x] Criar um campo e foundation_team na tabela de funcionarios ao invés de res_partner e associar a tabela foundation team com esse campo
- [X] criar departamento em manutenção automaticamente quando criar uma obra

- **Urgente para entrega**:
- [ ] Uma medição só pode ser excluida se nao tiver uma fatura relacionada
- [ ]  QUANDO CANCELAR UMA SALE ORDER TEM Q ARQUIVAR A OBRA
- [ ] Não pode fazer medição se o relatório não tiver assinatura
-
- [x] Entrega de obra a adriana tem que finalizar a obra na lista de obras, aí arquiva todos os registros relacionados
- [x] criar departamento em manutenção automaticamente quando criar uma obra e vincular a sale order e mostrar no kanban

- [ ] não pode ter mais de uma chamada para mesma maquina na mesma data
- [ ] o relatório deve buscar e relacionar com o primeiro / unico registro de chamada do mesmo dia
-**Cada modulo extende sale order e o analitico e estoque tem que herdar**

- Incluir botão se tem relatório na lista de chamdas da obra pra saber se teve produção ou não

- **Urgente para entrega**:
- [ ] Criar campo computado que verifica se o funcionario tava presente no dia em employee_assignment
- [ ]
