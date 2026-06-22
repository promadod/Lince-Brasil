from django.db import migrations, models


def ativar_conferencia_dinheiro(apps, schema_editor):
    FormaPagamentoLoja = apps.get_model('app_pdv', 'FormaPagamentoLoja')
    FormaPagamentoLoja.objects.filter(codigo='DINHEIRO').update(exige_conferencia=True)


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0029_loja_monitorar_entrega'),
    ]

    operations = [
        migrations.AddField(
            model_name='formapagamentoloja',
            name='exige_conferencia',
            field=models.BooleanField(
                default=False,
                help_text="Se marcado, exibe campo de troco na venda e botão 'Receber' no histórico.",
                verbose_name='Exige conferência de troco?',
            ),
        ),
        migrations.RunPython(ativar_conferencia_dinheiro, migrations.RunPython.noop),
    ]
