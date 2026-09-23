# Pipeline offline de IA

A IA é opcional e atua somente na preparação da base. Cada plano é processado isoladamente, a saída é gravada em `data/generated/` e passa por validação e revisão humana antes de qualquer consolidação em `data/reviewed/`.

O runtime não lê `data/generated/`: `app.py` consome a matriz revisada em `data/candidates.json`. Gemini, quando usado por uma ferramenta externa, recebe apenas o plano selecionado e nunca respostas de usuários. Chaves ficam fora do repositório.

Scripts:

- `extract_pdf_text.py`: extrai texto por página e calcula SHA-256; sinaliza OCR quando não houver texto.
- `validate_evidence.py`: valida registros contra o schema e bloqueia status não aprovado.
- `consolidate_matrix.py`: aceita somente evidências aprovadas para produzir uma matriz intermediária.
- `generate_question_candidates.py`: produz rascunhos para revisão humana; nunca publica perguntas automaticamente.
