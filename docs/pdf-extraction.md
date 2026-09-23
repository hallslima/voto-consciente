# Extração reproduzível dos planos de governo

## Escopo

Esta etapa transforma os oito PDFs locais em texto organizado por página. Ela não interpreta propostas, não classifica temas, não cria evidências políticas e não altera perguntas ou compatibilidades.

Os PDFs originais permanecem em `public/documents/government-plans/`. A saída é gravada em `data/generated/extracted-text/`, um JSON por `candidate_id`, e resumida em `data/generated/extraction_manifest.json`.

## Funcionamento

`extract_pdf_text.py` associa o `plan_document` de cada registro de `data/candidates.json` ao PDF local. Para cada arquivo, o processo:

1. calcula SHA-256 antes da leitura;
2. abre o documento com `pypdf`;
3. preserva a ordem e a numeração física das páginas, começando em 1;
4. extrai o texto sem correção ou interpretação;
5. registra método, totais, avisos e erros;
6. calcula novamente o SHA-256 e interrompe se o original tiver mudado;
7. grava o JSON e o manifesto.

O hash é calculado sobre os bytes integrais do PDF com `hashlib.sha256`. Ele identifica exatamente o arquivo processado e permite confirmar que o original não mudou.

## Estrutura e numeração

Cada item de `pages` contém `page_number`, `text` e `extraction_method`. `page_number: 1` corresponde à primeira página física entregue pelo leitor PDF; o número impresso visualmente no documento pode ser diferente. O método normal é `pypdf`; texto obtido pelo fallback é marcado `ocr-tesseract` página a página.

## Fallback de OCR

O OCR local é tentado somente em páginas sem texto quando `--ocr` é informado e as duas ferramentas estão no `PATH`:

- Poppler (`pdftoppm` ou `pdftocairo`) para renderizar a página a 300 DPI;
- Tesseract com o idioma `por` para reconhecer o texto.

O PDF original nunca é regravado. Imagens temporárias ficam em diretório temporário do sistema e são removidas ao final. O texto do OCR é preservado como retornado: palavras não são corrigidas por suposição.

Neste ambiente, Tesseract, Poppler, Pillow, `pdf2image` e `pytesseract` não estavam disponíveis. O plano de Raquel Lyra não possui camada textual extraível e, portanto, continua com status `requires_ocr`; sua extração não está concluída.

Em Windows, verifique os pacotes antes de autorizar a instalação:

```powershell
winget show --id UB-Mannheim.TesseractOCR --exact --source winget
winget show --id oschwartz10612.Poppler --exact --source winget
```

Após conferir fornecedor, versão e origem, a instalação explícita pode ser feita pelo responsável do ambiente:

```powershell
winget install --id UB-Mannheim.TesseractOCR --exact --source winget
winget install --id oschwartz10612.Poppler --exact --source winget
```

Reabra o terminal, confirme `Get-Command tesseract,pdftoppm` e verifique se o pacote de idioma português está instalado com `tesseract --list-langs`. Nenhuma dessas instalações é executada pelo projeto.

## Comandos para reprodução

Instale as dependências Python já declaradas pelo projeto e execute:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\extract_pdf_text.py --all --ocr
```

Para processar um PDF individual:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\extract_pdf_text.py public\documents\government-plans\ARQUIVO.pdf --candidate-id CANDIDATO --output data\generated\extracted-text\CANDIDATO.json --ocr
```

Compare os originais com os hashes gravados:

```powershell
Get-ChildItem public\documents\government-plans\*.pdf | Get-FileHash -Algorithm SHA256
```

Execute as verificações:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
npm.cmd run build
```

## Limitações

- PDF pode conter imagens, fontes defeituosas, objetos inconsistentes ou ordem de leitura diferente da visual.
- Página vazia pode ser intencional; `requires_ocr` é marcado quando nenhuma página do documento possui texto extraível.
- OCR pode trocar caracteres, perder colunas e alterar a ordem visual; sua saída exige validação humana posterior.
- O hash comprova identidade de bytes, não autenticidade política ou institucional da fonte.
- As URLs cadastradas atualmente levam à página inicial genérica do DivulgaCandContas; não há, no projeto, uma segunda versão oficial textual do plano de Raquel Lyra.

## Extração textual versus análise política

Extração textual copia texto e metadados técnicos do documento. Análise política seleciona evidências, interpreta ações, agrupa temas e compara posições. Esta etapa executa somente a primeira atividade. Os arquivos gerados não entram no runtime e não constituem evidências aprovadas.
