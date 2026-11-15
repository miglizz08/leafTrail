# Migrações do banco

O arquivo `../schema.sql` representa a estrutura atual usada para criar um banco novo. Depois que a tabela já existe, mudanças futuras no banco devem ser registradas em arquivos SQL incrementais nesta pasta.

## Convenção

- Nomeie os arquivos em ordem: `001_descricao.sql`, `002_descricao.sql` e assim por diante.
- Cada arquivo deve conter somente a mudança daquela etapa, sem recriar o banco inteiro.
- Antes de aplicar uma migration, confira se ela corresponde à próxima mudança ainda não aplicada.
- Aplique o SQL no banco local pelo phpMyAdmin e, em seguida, registre o arquivo no Git junto com o código relacionado.
- Nunca altere uma migration que já foi aplicada. Para corrigir ou mudar algo, crie uma nova migration.
- Atualize `../schema.sql` para refletir a estrutura mais recente, mantendo-o como referência para instalações novas.

O histórico das migrations versionadas no Git registra quais mudanças foram criadas. Por enquanto, a aplicação delas é manual pelo phpMyAdmin; não existe execução automática de migrations pelo Flask.
