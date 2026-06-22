# Deploy PythonAnywhere — checklist

Caminho no servidor: `/home/preapdev/Aplicativo-Delivery-SaaS/`

## Erro atual (site fora do ar)

```
ImportError: cannot import name 'produto_baixa_apenas_vasilhame_vazio' from 'app_pdv.models'
```

**Causa:** `views.py` foi atualizado, mas `models.py` no servidor ainda é a versão antiga.

**Correção imediata:** subir o arquivo `app_pdv/models.py` do seu PC e clicar em **Reload**.

---

## Arquivos que devem estar sincronizados (mesma versão local)

### Painel Gestor (API)
- [ ] `app_pdv/gestor_api.py` (NOVO)
- [ ] `app_pdv/gestor_views.py` (NOVO)
- [ ] `app_pdv/urls.py`
- [ ] `app_pdv/views.py`

### Obrigatório junto com views.py (senão o site não sobe)
- [ ] `app_pdv/models.py` ← **FALTANDO NO SERVIDOR**

### PDV / estoque (recomendado)
- [ ] `templates/app_pdv/vendas.html`
- [ ] `templates/app_pdv/detalhes_venda.html` (se usar observação)

### Migrations (console)
```bash
cd ~/Aplicativo-Delivery-SaaS
workon venv
python manage.py migrate
python manage.py check
```

Arquivos de migration se ainda não existirem no servidor:
- `app_pdv/migrations/0037_pagamento_dividido_liquidacaovenda.py`
- `app_pdv/migrations/0038_venda_vasilhame_vazio.py`
- `app_pdv/migrations/0039_loja_estoque_diario_log_fechamento.py`

---

## Após upload

1. Web → **Reload**
2. Teste: https://preapdev.pythonanywhere.com/
3. Teste API: `POST /api/login/` e `GET /api/gestor/resumo/` com Token

## Verificar no console (opcional)

```bash
cd ~/Aplicativo-Delivery-SaaS
python -c "from app_pdv.models import produto_baixa_apenas_vasilhame_vazio; print('OK')"
```

Se imprimir `OK`, o models.py está correto.
