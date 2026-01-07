# 🛒 Magno Distribuidora - Sistema PDV & Delivery (SaaS)

> Uma solução completa Full-Stack para gestão de distribuidoras, mercados e delivery, integrando Back-office web, PDV e Aplicativos Móveis.

![Status do Projeto](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Backend-Django-green)
![Flutter](https://img.shields.io/badge/Frontend-Flutter-blue)

## 📖 Sobre o Projeto

Este projeto é um sistema **SaaS (Software as a Service)** multi-lojas desenvolvido para gerenciar operações de varejo e atacado. O sistema centraliza o controle de estoque, financeiro e logística de entregas, oferecendo interfaces específicas para administradores, clientes finais e entregadores (motoboys).

A arquitetura foi pensada para ser escalável, permitindo que múltiplos estabelecimentos (lojas) operem na mesma base de dados com isolamento de dados.

---

## 🚀 Funcionalidades Principais

### 🏢 Back-office & Gestão (Django Admin Customizado)
* **Arquitetura Multi-Tenant:** Suporte a múltiplas lojas com gerentes e dados isolados.
* **Controle de Estoque Inteligente:**
    * Baixa automática de estoque na finalização da venda.
    * **Logística Reversa:** Estorno automático de estoque ao cancelar uma venda.
    * Alertas visuais de estoque baixo.
* **Gestão Financeira:**
    * Controle de Caixa (Abertura/Fechamento).
    * Registro de Receitas e Despesas categorizadas.
    * Relatórios de transações.
* **Impressão de Notas:** Geração de cupons não-fiscais otimizados para impressoras térmicas via CSS media print.

### 📱 Aplicativos Frontend (Flutter)
* **App do Cliente (Vitrine Virtual):**
    * Catálogo de produtos em tempo real.
    * Carrinho de compras e checkout.
    * **Smart Image Service:** Sistema inteligente de fallback para carregamento de imagens de produtos (busca por ID com contingência para ícones nativos em caso de falha).
* **App do Motoboy/Entregador:**
    * Gestão de entregas (Pendente, Em Rota, Entregue).
    * Conferência de recebimento de valores.
* **App PDV (Ponto de Venda):**
    * Interface ágil para vendas no balcão.

---

## 🛠️ Tecnologias Utilizadas

### Backend
* **Linguagem:** Python 3.10+
* **Framework:** Django 5.x
* **Banco de Dados:** SQLite (Dev) / PostgreSQL (Prod)
* **Infraestrutura:** PythonAnywhere (WSGI/Nginx)
* **Autenticação:** Sistema de usuários do Django extendido (PerfilUsuario).

### Frontend
* **Framework:** Flutter (Dart)
* **Plataformas:** Web (SPA), Android.
* **Gerenciamento de Estado:** `setState` (com arquitetura limpa e services isolados).
* **Integração:** Consumo de API RESTful (JSON).

---

## 📸 Screenshots

*(Espaço reservado para as imagens do projeto - Recomendo colocar aqui prints do Dashboard, da Tela de Vendas e do App Mobile)*

| Dashboard Admin | Vitrine Cliente | Detalhes da Venda |
|:---:|:---:|:---:|
| ![Dashboard](screenshots/dashboard_exemplo.png) | ![Vitrine](screenshots/vitrine_exemplo.png) | ![Venda](screenshots/venda_exemplo.png) |

---

## ⚙️ Como Executar o Projeto

### Pré-requisitos
* Python 3.10+
* Flutter SDK
* Git

### 1. Backend (Django)

```bash
# Clone o repositório
git clone [https://github.com/promadod/app-magno.git](https://github.com/promadod/app-magno.git)
cd app-magno

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Inicie o servidor
python manage.py runserver