# Generated manually — pagamento dividido e liquidações por parcela

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_pdv', '0036_loja_controla_vasilhame_itemestoque_vazios'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='permite_pagamento_dividido',
            field=models.BooleanField(
                default=False,
                help_text='Permite finalizar venda com 2 ou mais meios de liquidação (ex.: metade dinheiro, metade Pix).',
                verbose_name='Permitir pagamento dividido?',
            ),
        ),
        migrations.AddField(
            model_name='venda',
            name='pagamento_dividido',
            field=models.BooleanField(default=False, verbose_name='Pagamento dividido?'),
        ),
        migrations.AlterField(
            model_name='venda',
            name='meio_liquidacao',
            field=models.CharField(
                blank=True,
                choices=[
                    ('DINHEIRO', 'Dinheiro'),
                    ('PIX', 'Pix'),
                    ('CREDITO', 'Cartão de Crédito'),
                    ('DEBITO', 'Cartão de Débito'),
                    ('MISTO', 'Pagamento Dividido'),
                ],
                max_length=20,
                null=True,
                verbose_name='Meio de Liquidação',
            ),
        ),
        migrations.CreateModel(
            name='LiquidacaoVenda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('meio_liquidacao', models.CharField(
                    choices=[
                        ('DINHEIRO', 'Dinheiro'),
                        ('PIX', 'Pix'),
                        ('CREDITO', 'Cartão de Crédito'),
                        ('DEBITO', 'Cartão de Débito'),
                    ],
                    default='DINHEIRO',
                    max_length=20,
                    verbose_name='Meio de liquidação',
                )),
                ('troco_para', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('conferencia_ok', models.BooleanField(default=False)),
                ('data_liquidacao', models.DateTimeField(auto_now_add=True)),
                ('caixa', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='liquidacoes_venda', to='app_pdv.caixa', verbose_name='Turno de caixa',
                )),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pdv.loja')),
                ('registrado_por', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                    related_name='liquidacoes_venda_registradas', to=settings.AUTH_USER_MODEL,
                )),
                ('venda', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='liquidacoes', to='app_pdv.venda',
                )),
            ],
            options={
                'verbose_name': 'Liquidação de Venda',
                'verbose_name_plural': 'Liquidações de Venda',
                'ordering': ['id'],
            },
        ),
    ]
