# Generated manually — controle de botijões/galões vazios

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0035_pagamentofiado_caixa'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='controla_vasilhame_vazio',
            field=models.BooleanField(
                default=False,
                help_text='Ao vender, incrementa vasilhame vazio do item. Na entrada de estoque, '
                          'consome vazios ao reabastecer. Exibe coluna "Vazio" em /estoque/.',
                verbose_name='Controle de botijões/galões vazios?',
            ),
        ),
        migrations.AddField(
            model_name='itemestoque',
            name='quantidade_vazios',
            field=models.DecimalField(
                decimal_places=3,
                default=0.0,
                max_digits=10,
                verbose_name='Vasilhame vazio (botijões/galões)',
            ),
        ),
    ]
