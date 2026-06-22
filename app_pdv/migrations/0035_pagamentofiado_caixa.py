# Generated manually — vincular pagamentos fiado ao turno de caixa

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0034_vendas_fiado'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagamentofiado',
            name='caixa',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='pagamentos_fiado', to='app_pdv.caixa', verbose_name='Turno de caixa',
            ),
        ),
    ]
