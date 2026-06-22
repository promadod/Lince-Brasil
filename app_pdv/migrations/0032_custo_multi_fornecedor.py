# Generated manually for multi-supplier cost phases 1-3

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0031_venda_meio_liquidacao'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrecoFornecedorItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preco_compra', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Preço de custo (unitário do item)')),
                ('ativo', models.BooleanField(default=True)),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='precos_itens', to='app_pdv.fornecedor')),
                ('item_estoque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='precos_fornecedor', to='app_pdv.itemestoque')),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_pdv.loja')),
            ],
            options={
                'verbose_name': 'Preço por Fornecedor',
                'verbose_name_plural': 'Preços por Fornecedor',
                'ordering': ['fornecedor__nome'],
                'unique_together': {('item_estoque', 'fornecedor')},
            },
        ),
        migrations.AddField(
            model_name='entradaestoque',
            name='fornecedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_pdv.fornecedor', verbose_name='Fornecedor'),
        ),
        migrations.AddField(
            model_name='entradaestoque',
            name='preco_unitario_compra',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Preço unitário de compra'),
        ),
        migrations.AddField(
            model_name='itemvenda',
            name='custo_unitario',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Custo unitário (snapshot na venda)'),
        ),
    ]
