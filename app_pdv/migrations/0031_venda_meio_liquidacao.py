from django.db import migrations, models

MEIOS_VALIDOS = {'DINHEIRO', 'PIX', 'CREDITO', 'DEBITO'}


def popular_meio_liquidacao(apps, schema_editor):
    Venda = apps.get_model('app_pdv', 'Venda')
    for venda in Venda.objects.all():
        if venda.forma_pagamento in MEIOS_VALIDOS:
            venda.meio_liquidacao = venda.forma_pagamento
        elif venda.forma_pagamento:
            venda.meio_liquidacao = 'PIX'
        else:
            venda.meio_liquidacao = 'PIX'
        venda.save(update_fields=['meio_liquidacao'])


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0030_formapagamentoloja_exige_conferencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='venda',
            name='meio_liquidacao',
            field=models.CharField(
                blank=True,
                choices=[
                    ('DINHEIRO', 'Dinheiro'),
                    ('PIX', 'Pix'),
                    ('CREDITO', 'Cartão de Crédito'),
                    ('DEBITO', 'Cartão de Débito'),
                ],
                max_length=20,
                null=True,
                verbose_name='Meio de Liquidação',
            ),
        ),
        migrations.RunPython(popular_meio_liquidacao, migrations.RunPython.noop),
    ]
