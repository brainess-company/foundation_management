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
- [x] Definir o metodo que atualiza a lista de obras com base nas sale_order 
- [x] Definir vicualização xml para operador clicar na foundation_obra e inserir estaca produzida
- [x] O campo diâmtro na estca não pode ser um campo aberto deve ser uma lista da descrição da variavel de produto (string) do produto em questão
- [x] Retornar o campo de preço unitario relacionado ao diâmtro selecionado
- [x] Calcular o valor da estaca multiplicando a profundidade pelo preço unitário
- [ ] Inserir um filtro no notebook que o funcionario vai usar para inserir estaca só aparecer as que estão relacionadas com o serviço que ele está alocado, na tela de estacas já está assim automaticamente.
- [ ] Melhorar kanban
- [ ] Enviar medição para conferência de terceiros igual a sale_order
- [ ] Inserir assinatura
- [ ] Definir permissões de segurança

