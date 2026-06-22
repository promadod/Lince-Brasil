# Generated manually — vendas fiado (depósito de gás)

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_pdv', '0033_alter_venda_forma_pagamento'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='usa_fiado',
            field=models.BooleanField(
                default=False,
                help_text='Ativa venda a prazo no PDV (ex.: depósito de gás). Lojas sem esta opção continuam com o fluxo normal de pagamento integral.',
                verbose_name='Habilitar Vendas Fiado?',
            ),
        ),
        migrations.AddField(
            model_name='venda',
            name='eh_fiado',
            field=models.BooleanField(default=False, verbose_name='Venda Fiado?'),
        ),
        migrations.AlterField(
            model_name='venda',
            name='status',
            field=models.CharField(
                choices=[
                    ('ABERTO', 'Em Aberto (Balcão)'),
                    ('FINALIZADO', 'Finalizado'),
                    ('ORCAMENTO', 'Orçamento'),
                    ('PENDENTE', 'Aguardando Aprovação'),
                    ('EM_PREPARACAO', 'Em Separação'),
                    ('SAIU_ENTREGA', 'Saiu para Entrega'),
                    ('CANCELADO', 'Cancelado/Recusado'),
                    ('AGUARDANDO_FINALIZAR', 'Pausado / Finalizar Depois'),
                    ('FIADO', 'Fiado (Pagamento Pendente)'),
                ],
                default='ABERTO',
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='PagamentoFiado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('data_pagamento', models.DateTimeField(auto_now_add=True)),
                ('meio_liquidacao', models.CharField(
                    choices=[('DINHEIRO', 'Dinheiro'), ('PIX', 'Pix'), ('CREDITO', 'Cartão de Crédito'), ('DEBITO', 'Cartão de Débito')],
                    default='DINHEIRO', max_length=20, verbose_name='Meio de liquidação',
                )),
                ('observacao', models.CharField(blank=True, max_length=200, null=True)),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pdv.loja')),
                ('registrado_por', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='pagamentos_fiado_registrados', to=settings.AUTH_USER_MODEL,
                )),
                ('venda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagamentos_fiado', to='app_pdv.venda')),
            ],
            options={
                'verbose_name': 'Pagamento Fiado',
                'verbose_name_plural': 'Pagamentos Fiado',
                'ordering': ['-data_pagamento'],
            },
        ),
    ]
