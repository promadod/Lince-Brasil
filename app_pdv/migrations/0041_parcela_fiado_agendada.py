from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_pdv', '0040_rename_app_pdv_log_loja_dat_tipo_idx_app_pdv_log_loja_id_ce16db_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParcelaFiadoAgendada',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_vencimento', models.DateField(verbose_name='Vencimento')),
                ('data_entrada', models.DateTimeField(auto_now_add=True, verbose_name='Data de agendamento')),
                ('status', models.CharField(
                    choices=[('AGENDADO', 'Agendado'), ('PAGO', 'Pago'), ('CANCELADO', 'Cancelado')],
                    default='AGENDADO', max_length=20,
                )),
                ('observacao', models.CharField(blank=True, max_length=200, null=True)),
                ('cliente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parcelas_fiado_agendadas', to='app_pdv.cliente',
                )),
                ('criado_por', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='parcelas_fiado_criadas', to=settings.AUTH_USER_MODEL,
                )),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pdv.loja')),
                ('pagamento', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='parcela_agendada', to='app_pdv.pagamentofiado',
                )),
                ('venda', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='parcelas_fiado_agendadas', to='app_pdv.venda',
                )),
            ],
            options={
                'verbose_name': 'Parcela Fiado Agendada',
                'verbose_name_plural': 'Parcelas Fiado Agendadas',
                'ordering': ['data_vencimento', 'id'],
            },
        ),
    ]
