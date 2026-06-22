from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_pdv', '0038_venda_vasilhame_vazio'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='estoque_diario',
            field=models.BooleanField(
                default=False,
                help_text='Permite editar cheios/vazios em /estoque/, registra abertura/fechamento do dia e usa esses saldos no PDV. Requer controle de vasilhame ativo.',
                verbose_name='Estoque diário (contagem manual)?',
            ),
        ),
        migrations.CreateModel(
            name='LogFechamentoEstoqueDiario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_referencia', models.DateField(verbose_name='Data de referência')),
                ('tipo', models.CharField(choices=[('ABERTURA', 'Abertura do dia'), ('FECHAMENTO', 'Fechamento do dia')], max_length=12)),
                ('quantidade_cheios', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('quantidade_vazios', models.DecimalField(decimal_places=3, default=0, max_digits=10)),
                ('registrado_em', models.DateTimeField(auto_now_add=True)),
                ('item_estoque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs_fechamento_diario', to='app_pdv.itemestoque')),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs_estoque_diario', to='app_pdv.loja')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Log de estoque diário',
                'verbose_name_plural': 'Logs de estoque diário',
                'ordering': ['-registrado_em', 'item_estoque__nome'],
            },
        ),
        migrations.AddIndex(
            model_name='logfechamentoestoqueDiario',
            index=models.Index(fields=['loja', 'data_referencia', 'tipo'], name='app_pdv_log_loja_dat_tipo_idx'),
        ),
    ]
