# Leaf Trail

Aplicação web para registrar e acompanhar gastos pessoais. O projeto usa Flask e MySQL, com interface responsiva para celular e computador.

## Funcionalidades

- Cadastrar gastos com data, valor, categoria e descrição opcional.
- Listar, editar e excluir gastos.
- Exibir o total dos gastos cadastrados.
- Validar os dados no servidor antes de gravar.

## Tecnologias

- Python 3.13 e Flask
- MySQL Connector/Python
- MySQL local pelo XAMPP
- TiDB Cloud Starter, compatível com o protocolo MySQL, para o banco usado pela aplicação publicada
- HTML, CSS e templates Jinja
- pytest e Playwright para testes
- GitHub Actions para executar os testes em push e pull request
- Render para hospedar a aplicação web

## Requisitos

- Python 3.13+
- Git
- XAMPP para executar o MySQL localmente, ou acesso a um banco compatível com MySQL

## Instalação local no Windows

No PowerShell, na pasta do projeto:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Se o PowerShell bloquear a ativação do ambiente virtual, use diretamente os executáveis em `venv\Scripts\` ou ajuste a política de execução conforme a configuração do seu Windows.

## Configuração do banco local

1. Inicie o MySQL no XAMPP. Inicie também o Apache se for usar o phpMyAdmin.
2. No phpMyAdmin, execute o conteúdo de [`database/schema.sql`](database/schema.sql) para criar o banco `leaftrail` e a tabela `gastos`.
3. Edite o arquivo `.env` com os dados do seu MySQL local. O arquivo `.env` é ignorado pelo Git e não deve ser enviado ao repositório.

Variáveis usadas pela aplicação:

| Variável | Descrição | Exemplo local |
|---|---|---|
| `DB_HOST` | Endereço do servidor do banco | `127.0.0.1` |
| `DB_PORT` | Porta do MySQL; se omitida, usa `3306` | `3306` |
| `DB_NAME` | Nome do banco | `leaftrail` |
| `DB_USER` | Usuário do MySQL | `leaftrail_app` |
| `DB_PASSWORD` | Senha do usuário do MySQL | Configure no `.env` |
| `DB_SSL_CA` | Caminho do certificado CA para TLS verificado; opcional | Não definir para o MySQL local |

O `.env.example` contém valores de exemplo. Troque-os pelos dados do seu ambiente antes de executar o app.

## Executar a aplicação

Com o ambiente virtual ativo e o MySQL ligado:

```powershell
python app.py
```

Abra no navegador o endereço local indicado no terminal. A porta local pode variar conforme a configuração de `app.py`.

## Banco remoto e Render

A aplicação publicada usa uma instância TiDB Cloud Starter no modo compatível com MySQL. No painel da Render, configure as mesmas variáveis na página **Environment** do serviço `leaftrail`:

| Variável | Valor para o TiDB Cloud |
|---|---|
| `DB_HOST` | Host exibido na tela **Connect** do TiDB |
| `DB_PORT` | `4000` |
| `DB_NAME` | `leaftrail` |
| `DB_USER` | Usuário mostrado pelo TiDB, incluindo o prefixo da instância |
| `DB_PASSWORD` | Senha da instância TiDB |
| `DB_SSL_CA` | `/etc/ssl/certs/ca-certificates.crt` |

O código ativa a verificação do certificado e da identidade do servidor quando `DB_SSL_CA` está definida. Configure valores secretos, como `DB_PASSWORD`, diretamente na Render; nunca os coloque no código ou no Git. Salve as variáveis e faça o serviço redeployar para aplicá-las.

O serviço Render publica a branch `layout-novo-gasto`. A configuração de deploy fica em [`render.yaml`](render.yaml).

## Testes

Execute os testes unitários e E2E com:

```powershell
python -m pytest
```

O teste E2E abre Chromium pelo Playwright e usa um armazenamento em memória isolado; ele não altera o banco configurado no `.env`. Para instalar o navegador localmente uma vez:

```powershell
python -m playwright install chromium
```

O GitHub Actions instala as dependências do navegador e executa a suíte em pushes e pull requests.

## Banco de dados e migrations

`database/schema.sql` é a estrutura de referência para criar um banco novo. Alterações futuras devem ser registradas como arquivos SQL numerados em `database/migrations/` e aplicadas manualmente. Consulte [`database/migrations/README.md`](database/migrations/README.md) para a convenção.

O app valida no servidor que o valor seja positivo, que a data seja válida, que a categoria esteja na lista permitida e que a descrição tenha no máximo 255 caracteres. O TiDB Starter deixa a restrição SQL `CHECK` desativada por padrão; portanto, essa regra de valor é aplicada pelo app, não por uma restrição ativa no banco. Evite inserir gastos diretamente no banco sem essas validações.

## Decisões e limitações atuais

- A aplicação usa Flask e templates do servidor; não há uma API separada.
- O MySQL do XAMPP é para desenvolvimento local. A Render precisa de um banco remoto porque não consegue acessar o MySQL instalado no computador do usuário.
- O TiDB Cloud Starter implementa o protocolo e recursos comuns do MySQL usados pelo app, com cotas gratuitas mensais. Ao atingir uma cota, novas conexões podem ser temporariamente bloqueadas.
- As migrations ainda são executadas manualmente; o Flask não as aplica durante a inicialização.
- Autenticação e dados separados por usuário ainda não fazem parte do MVP.
