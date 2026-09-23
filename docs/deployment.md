# Publicação no Netlify e Render

## Arquitetura

O frontend React/Vite é publicado como site estático no Netlify. A API FastAPI é um Web Service separado no Render. O navegador chama a API pela URL definida em `VITE_API_BASE_URL`.

Fotos (`/assets/candidates/...`) e PDFs (`/documents/government-plans/...`) pertencem ao diretório `public` e são publicados pelo Netlify. Os caminhos relativos retornados por `/api/bootstrap` continuam apontando para o domínio do frontend; eles não dependem do filesystem efêmero do Render.

## 1. Publicar o backend no Render

1. Conecte o repositório e crie um Blueprint a partir de `render.yaml`, na branch `main`.
2. Confirme o runtime Python e a versão `3.13.5` definida por `PYTHON_VERSION`.
3. O build command é `pip install -r requirements.txt`.
4. O start command é `uvicorn app:app --host 0.0.0.0 --port $PORT`.
5. O health check é `/api/health`.
6. Cadastre `FRONTEND_ORIGINS` com as origens autorizadas, separadas por vírgula. Não use `*`.

O serviço não requer banco de dados nem disco persistente. O auto deploy acompanha novos commits da branch `main`.

## 2. Publicar o frontend no Netlify

1. Importe o mesmo repositório e selecione a branch `main`.
2. Use `npm run build` como build command e `dist` como publish directory.
3. Cadastre `VITE_API_BASE_URL` com a origem do Render, por exemplo `https://voto-consciente-api.onrender.com`, sem caminho adicional.
4. Publique. A regra final de rewrite em `netlify.toml` direciona rotas do SPA para `index.html`.

O Netlify não executa o FastAPI. Em desenvolvimento, a ausência de `VITE_API_BASE_URL` usa `http://127.0.0.1:8000`.

## Ordem e configuração de CORS

1. Publique o Render e obtenha a URL da API.
2. Configure essa URL em `VITE_API_BASE_URL` no Netlify e publique o frontend.
3. Copie a origem final do Netlify (somente esquema e host, sem barra final) para `FRONTEND_ORIGINS` no Render.
4. Salve a variável e aguarde a nova implantação do backend.
5. Se houver domínio personalizado ou deploy de produção adicional, acrescente sua origem à lista separada por vírgulas.

As origens locais `127.0.0.1` e `localhost` nas portas 5173 e 5174 sempre são preservadas. Previews do Netlify não são liberados implicitamente; inclua uma origem de preview conscientemente quando precisar testá-la.

## Testes após a publicação

- API: abra `https://SEU-BACKEND.onrender.com/api/health`; a resposta saudável contém `"ok": true`.
- Dados: abra `/api/bootstrap` no backend e confirme perguntas e candidaturas.
- Cálculo: conclua o questionário pelo domínio Netlify e verifique a requisição `POST /api/results` no painel de rede do navegador.
- Fotos: abra no Netlify um caminho retornado pela API, como `/assets/candidates/...jpg`.
- PDFs: abra no Netlify um caminho retornado pela API, como `/documents/government-plans/...pdf`, e confirme que o link externo abre o documento.
- CORS: no console do navegador, confirme que não há bloqueios e que o cabeçalho `Access-Control-Allow-Origin` corresponde exatamente ao frontend.

## Variáveis de ambiente

| Serviço | Variável | Exemplo |
|---|---|---|
| Netlify | `VITE_API_BASE_URL` | `https://voto-consciente-api.onrender.com` |
| Render | `FRONTEND_ORIGINS` | `https://voto-consciente-pe.netlify.app` |

Esses valores são configurações, não segredos. Ainda assim, não grave URLs específicas de uma implantação nos fontes. Arquivos `.env` reais permanecem ignorados pelo Git; `.env.example` contém apenas exemplos locais.

## Atualização e rollback

Commits incorporados à `main` disparam as publicações automáticas nos dois serviços. Para rollback, restaure um deploy anterior no painel do Netlify e outro no painel do Render. Como os serviços são independentes, reverta ambos quando uma alteração modificar o contrato da API. Não altere os dados auditados para executar um rollback.

## Limitações e preparação da demonstração

Planos gratuitos podem impor cotas, filas de build e suspensão por inatividade; o primeiro acesso ao Render pode ter latência de inicialização. Eles também não oferecem garantia de disponibilidade adequada a sistemas críticos.

Antes da demonstração:

1. acesse `/api/health` para aquecer e validar o backend;
2. carregue o frontend e conclua uma simulação;
3. abra uma foto e um PDF;
4. confirme no navegador a ausência de erros de CORS;
5. mantenha o procedimento local documentado em `docs/demo-script.md` como contingência.
