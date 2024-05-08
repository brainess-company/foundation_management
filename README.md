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
- [x] Incluir gerenciamento de equipe onde cada funcionario está relacionado a uma equipe (Máquina)
- [x] E quando for pra ter mais de uma maquina relacionada a um serviço?
- [x] Pra cada serviço só pode ter uma máquina relacionada mas não é assim que deve funcionar
- [x] Incluir um status no formulario de maquina, Em mobilização, etc
- [x] Quando uma sale order virar uma obra, criar uma account move para cada tipo de item e uma generica
- [x] Lista de presenças (Nao fica salvo nada para o proximo dia, se nao, o operador não preenche, só dá ok e ja era)
- [X] Cada relatorio deve ter um nome composto de Relatorio para cada foundation_maquina_registro
- [x] Colocar filtro de estacas por serviço no relatorio que o operador preenche

- **Futuramente**:
- [ ] Baixar medição em pdf para enviar ao cliente
- [ ] Da pra fazer um endereço clicado abrir no google maps
- [ ] Configurar profundidade minima e máxima
- [ ] Tenho que criar um estoque de saída para a obra mesmo mas quando for feita uma transferencia para ele, a entrega seja feita automatica, e ele deve receber o campo da conta analitica da maquina serviço obra relacionada
- [ ] incluir botão no kanbam para deixar a transferencia pronta
- [ ] Métrica chamada unidades de trabalho, e trabalhadores distintos no período, verificar correlações
- [ ] Estudar o relacionamento com o portal do cliente
- [ ] No portal do cliente aparece todos os projetos relacionados com o cliente se o modulo de fundações criar um projeto o cliente pode acompanhar
- [ ] Criar campo de calculo relativo no produto (area da base de um diametro da estaca) esse valor será multiplicado pela quantidade executada

- [ ] Vincular purchase_order com maintenance_request (uma unica manutenção pode ter varios pedidos de compras relacionados)
- [ ] Quando o Lucas fizer uma purchase_order selecionar com qual ou quais manutenções essa compra está relacionada.
- [ ] Vincular purchase_order com maintenance_request (uma unica manutenção pode ter varios pedidos de compras relacionados)
- [ ] Quando o Lucas fizer uma purchase_order selecionar com qual ou quais manutenções essa compra está relacionada.

- [x] Opção de gerar medição pelos relatorios?
- [x] Depois que o relatorio for salvo a assinatura fica read only
- [x] Definir permissões de segurança
- [x] Quando uma medição for excluida as estecas tem que ser desrelacionadas com a medição
- [x] Remover botões de ação desnecessários
- [x] No cadastro de máquinas a adriana seleciona se a maquina precisa de lista de chamada


- **Urgente**:

- [X] Falta incluir o proprio operador na lista de chamada
- [X] Falta criar grupos de permissões
- [X] Quando criar conta analitica automaticamente criar um estoque central se não houver e associar todas as empresas a e automaticamente criar um estoque para a obra
- [X] Criar um campo e foundation_team na tabela de funcionarios ao invés de res_partner e associar a tabela foundation team com esse campo
- [x] Uma estaca só pode ser medida se o relatorio relacionado estiver no estágio confirmado
- [x] Uma medição só pode gerar uma unica fatura
- [x] Criar um campo e foundation_team na tabela de funcionarios ao invés de res_partner e associar a tabela foundation team com esse campo
- [x] Falta incluir o proprio operador na lista de chamada
- [x] Falta incluir o operador na propria equipe
- [X] criar departamento em manutenção automaticamente quando criar uma obra 
- [x] Uma medição só pode gerar uma unica fatura

- **Urgente para entrega**:
- [ ] Falta testar os efeitos cascata de deleções de arquivos (quando, arquivar um relatorio, deduzir as quantidades da sale order)
- [ ] quando for feita uma transferencia para estoque de saída, a entrega seja feita automatica, e ele deve receber o campo da conta analitica da maquina serviço obra relacionada
- [ ] Criar view para departamento criado, o luigi precisa ver quais serviços serão executados na obra, o departamento precisa estar vinculado com a sale_order  Ou criar projeto no sistema
- [ ] Uma medição só pode ser excluida se nao tiver uma fatura relacionada

- [x] Falta criar grupos de permissões
- [x] Entrega de obra a adriana tem que finalizar a obra na lista de obras, aí arquiva todos os registros relacionados
- [x] criar departamento em manutenção automaticamente quando criar uma obra e vincular a sale order e mostrar no kanban

