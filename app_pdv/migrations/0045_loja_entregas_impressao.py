from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0044_produto_usa_venda_completa'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='trabalha_com_entregas',
            field=models.BooleanField(
                default=True,
                help_text='Sim: vendas com cliente podem ir para entrega. Não: vendas no PDV ficam como venda na loja (balcão), mesmo com cliente.',
                verbose_name='Trabalha com entregas?',
            ),
        ),
        migrations.AddField(
            model_name='loja',
            name='impressao_automatica',
            field=models.BooleanField(
                default=False,
                help_text='Sim: ao finalizar venda no PDV, abre a impressão da nota fiscal.',
                verbose_name='Impressão automática ao finalizar venda?',
            ),
        ),
    ]
