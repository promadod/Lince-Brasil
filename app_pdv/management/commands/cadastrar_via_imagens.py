import os
from django.core.management.base import BaseCommand
from app_pdv.models import ItemEstoque, Produto
from django.conf import settings

class Command(BaseCommand):
    help = 'Cadastra produtos automaticamente baseado nos arquivos da pasta de imagens'

    def handle(self, *args, **kwargs):
        
        CAMINHO_IMAGENS = 'C:/projetos flutter/app_magno/assets/produtos' 
        
        if not os.path.exists(CAMINHO_IMAGENS):
            self.stdout.write(self.style.ERROR(f'Pasta não encontrada: {CAMINHO_IMAGENS}'))
            return

        arquivos = [f for f in os.listdir(CAMINHO_IMAGENS) if f.endswith('.png')]
        
        count_criados = 0
        count_existentes = 0

        self.stdout.write(f"Encontrei {len(arquivos)} imagens. Iniciando cadastro...")

        for arquivo in arquivos:
            
            nome_limpo = arquivo.replace('.png', '').replace('_', ' ').title()
            
            
            try:
                
                item, created_item = ItemEstoque.objects.get_or_create(
                    nome=nome_limpo,
                    defaults={'quantidade_estoque': 0}
                )

                
                nome_venda = f"{nome_limpo}" 
                
                if not Produto.objects.filter(item_estoque=item).exists():
                   
                    Produto.objects.create(
                        item_estoque=item,
                        nome_venda=nome_venda,
                        preco_compra=0.01, 
                        preco_venda=1.00,  
                        quantidade_baixa=1
                    )
                    self.stdout.write(self.style.SUCCESS(f'✅ Criado: {nome_venda}'))
                    count_criados += 1
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️ Já existe: {nome_venda}'))
                    count_existentes += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Erro ao processar {nome_limpo}: {e}'))

        self.stdout.write(self.style.SUCCESS('----------------------------------'))
        self.stdout.write(self.style.SUCCESS(f'Processo Finalizado!'))
        self.stdout.write(f'Novos Produtos: {count_criados}')
        self.stdout.write(f'Já Existiam: {count_existentes}')