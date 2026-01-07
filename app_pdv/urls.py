from django.urls import path
from . import views
from .views import CustomAuthToken,EntregasDisponiveisView, AssumirEntregaView, MinhasEntregasView

urlpatterns = [
    #--------------------------------Dashboard-----------------------------

    path('', views.dashboard, name='dashboard'),

    # ------------------------------Produtos------------------------------

    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/novo/', views.gerenciar_produto, name='novo_produto'),
    path('produtos/editar/<int:id>/', views.gerenciar_produto, name='editar_produto'),
    path('produtos/deletar/<int:id>/', views.deletar_produto, name='deletar_produto'),

    # ------------------------------Clientes------------------------------

    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/novo/', views.gerenciar_cliente, name='novo_cliente'),
    path('clientes/editar/<int:id>/', views.gerenciar_cliente, name='editar_cliente'),
    path('clientes/deletar/<int:id>/', views.deletar_cliente, name='deletar_cliente'),

    # ------------------------------Vendas------------------------------

    path('vendas/nova/', views.nova_venda, name='nova_venda'),
    path('vendas/salvar/', views.salvar_venda, name='salvar_venda'),
    path('vendas/excluir/<int:id>/', views.excluir_venda, name='excluir_venda'),

    # ------------------------------Fornecedores------------------------------

    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.gerenciar_fornecedor, name='novo_fornecedor'),
    path('fornecedores/editar/<int:id>/', views.gerenciar_fornecedor, name='editar_fornecedor'),
    path('fornecedores/deletar/<int:id>/', views.deletar_fornecedor, name='deletar_fornecedor'),

    # ------------------------------Lojas------------------------------

    path('lojas/', views.lista_lojas, name='lista_lojas'),
    path('lojas/novo/', views.gerenciar_loja, name='nova_loja'),
    path('lojas/editar/<int:id>/', views.gerenciar_loja, name='editar_loja'),

    # ------------------------------Vendas (PDV)------------------------------

    path('vendas/nova/', views.nova_venda, name='nova_venda'),
    path('vendas/salvar/', views.salvar_venda, name='salvar_venda'),
    path('vendas/retomar/<int:id>/', views.retomar_venda, name='retomar_venda'),
    path('vendas/cancelar/<int:id>/', views.cancelar_venda_pdv, name='cancelar_venda_pdv'),
    
    # ------------------------------Histórico ------------------------------

    path('vendas/historico/', views.lista_vendas, name='lista_vendas'),
    path('vendas/detalhes/<int:id>/', views.detalhes_venda, name='detalhes_venda'),

    # ------------------------------Caixa------------------------------

    path('caixa/', views.fluxo_caixa, name='fluxo_caixa'),
    path('caixa/fechar/', views.fechar_caixa, name='fechar_caixa'),
    path('caixa/recibo/<int:id>/', views.ver_recibo_fechamento, name='ver_recibo_fechamento'),

    # ------------------------------Estoque------------------------------ 


    path('estoque/', views.lista_estoque, name='lista_estoque'),
    path('estoque/adicionar/', views.adicionar_estoque, name='adicionar_estoque'),

    # ------------------------------Itens------------------------------

    path('itens/', views.lista_itens, name='lista_itens'),
    path('itens/novo/', views.gerenciar_item, name='novo_item'),
    path('itens/editar/<int:id>/', views.gerenciar_item, name='editar_item'),
    path('itens/deletar/<int:id>/', views.deletar_item, name='deletar_item'),


    # ------------------------------Relatórios e Financeiro------------------------------

    path('relatorios/', views.relatorios, name='relatorios'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/deletar/<int:id>/', views.deletar_categoria, name='deletar_categoria'),
    path('transacao/nova/', views.adicionar_transacao, name='adicionar_transacao'),
    path('dashboard/relatorios/entregas/', views.relatorio_entregadores, name='relatorio_entregas'),



    # ------------------------------Importação------------------------------
    path('importacao/', views.menu_importacao, name='menu_importacao'),
    path('importacao/clientes/', views.importar_clientes, name='importar_clientes'),
    path('importacao/produtos/', views.importar_produtos, name='importar_produtos'),

    # ------------------------------Vendedor------------------------------
    path('vendedores/', views.lista_vendedores, name='lista_vendedores'),
    path('vendedores/cadastrar/', views.cadastrar_vendedor, name='cadastrar_vendedor'),

    # ------------------------------Entregas------------------------------
    path('entregas/', views.lista_entregas, name='lista_entregas'),
    path('entregas/motoboy/novo/', views.cadastrar_motoboy, name='cadastrar_motoboy'),
    path('entregas/moto/nova/', views.cadastrar_moto, name='cadastrar_moto'),
    path('vendas/confirmar-motoboy/<int:venda_id>/', views.confirmar_recebimento_motoboy, name='confirmar_recebimento_motoboy'),

    # ------------------------------ROTA DA API (Flutter OBS: Motobot / Diretor)------------------------------

    path('api/login/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/entregas/assumir/<int:venda_id>/', AssumirEntregaView.as_view(), name='api_assumir_entrega'),
    path('api/entregas/minhas/', MinhasEntregasView.as_view(), name='api_minhas_entregas'),
    path('api/entregas/disponiveis/', EntregasDisponiveisView.as_view(), name='api_listar_entregas'),
    path('api/entregas/finalizar/<int:venda_id>/', views.api_finalizar_entrega, name='api_finalizar_entrega'),
    path('api/entregas/ganhos/', views.api_meus_ganhos, name='api_meus_ganhos'),


    # ------------------------------APP Clientes ------------------------------

    path('torre-controle/', views.torre_controle, name='torre_controle'),
    path('api/torre/pedidos/', views.api_pedidos_torre, name='api_pedidos_torre'),
    path('api/torre/atualizar/<int:venda_id>/', views.api_atualizar_status_pedido, name='api_atualizar_status'),
    path('api/produtos/', views.api_listar_produtos, name='api_listar_produtos'),
    path('api/pedido/criar/', views.api_criar_pedido, name='api_criar_pedido'),
    path('api/cliente/buscar/', views.api_buscar_cliente, name='api_buscar_cliente'),
    path('api/cliente/pedidos/', views.api_meus_pedidos, name='api_meus_pedidos'),
    path('api/venda/conferir/<int:venda_id>/', views.api_conferir_venda, name='api_conferir_venda'),

    # ------------------------------Torre de Controle (APP CLIENTES)------------------------------

    path('torre-controle/', views.torre_controle, name='torre_controle'),
    path('api/torre/dados/', views.api_pedidos_torre,name='api_pedidos_torre'),
    path('api/pedido/status/<int:venda_id>/', views.api_atualizar_status_pedido, name='api_atualizar_status'),
    path('api/taxa_entrega/', views.api_obter_taxa_entrega, name='api_obter_taxa_entrega'),
    path('config/definir_taxa/', views.definir_taxa_entrega, name='definir_taxa_entrega'),
    path('torre-controle/', views.torre_controle, name='app_vendas'),
    path('api/loja/toggle/', views.api_toggle_loja, name='api_toggle_loja'),


]