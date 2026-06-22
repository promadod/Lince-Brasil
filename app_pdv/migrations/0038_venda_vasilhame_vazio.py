from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0037_pagamento_dividido_liquidacaovenda'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='vende_vasilhame_vazio',
            field=models.BooleanField(
                default=False,
                help_text='Produto de venda de botijão/galão vazio. Baixa apenas o estoque de vazios.',
                verbose_name='Vende vasilhame vazio',
            ),
        ),
        migrations.AddField(
            model_name='itemvenda',
            name='baixa_vasilhame_vazio',
            field=models.BooleanField(
                default=False,
                help_text='Snapshot: esta linha deduziu estoque de vazios, não de cheios.',
                verbose_name='Baixa de vasilhame vazio',
            ),
        ),
    ]
