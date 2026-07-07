from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0045_loja_entregas_impressao'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='cobra_taxa_servico',
            field=models.BooleanField(
                default=False,
                help_text="Ativo com 'Trabalha com entregas' desmarcado: aplica % sobre o consumo no PDV e na nota.",
                verbose_name='Cobra taxa de serviço sobre a venda?',
            ),
        ),
        migrations.AddField(
            model_name='loja',
            name='taxa_servico_pct',
            field=models.DecimalField(
                decimal_places=2, default=10.0, max_digits=5,
                verbose_name='Taxa de serviço padrão (%)',
            ),
        ),
        migrations.AddField(
            model_name='venda',
            name='taxa_servico',
            field=models.DecimalField(
                decimal_places=2, default=0.0, max_digits=10,
                verbose_name='Valor taxa de serviço (R$)',
            ),
        ),
        migrations.AddField(
            model_name='venda',
            name='taxa_servico_pct',
            field=models.DecimalField(
                decimal_places=2, default=0.0, max_digits=5,
                verbose_name='Taxa de serviço (%) aplicada',
            ),
        ),
    ]
