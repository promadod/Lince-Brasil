from django.db import migrations, models
import django.db.models.deletion


FORMAS_PAGAMENTO_PADRAO = [
    {'codigo': 'DINHEIRO', 'nome': 'Dinheiro', 'cor': '#28a745', 'icone': 'fa-money-bill-wave', 'ordem': 1},
    {'codigo': 'PIX', 'nome': 'Pix', 'cor': '#03dac6', 'icone': 'fa-qrcode', 'ordem': 2},
    {'codigo': 'CREDITO', 'nome': 'Cartão de Crédito', 'cor': '#29b6f6', 'icone': 'fa-credit-card', 'ordem': 3},
    {'codigo': 'DEBITO', 'nome': 'Cartão de Débito', 'cor': '#ff9800', 'icone': 'fa-wallet', 'ordem': 4},
]


def criar_formas_padrao_existentes(apps, schema_editor):
    Loja = apps.get_model('app_pdv', 'Loja')
    FormaPagamentoLoja = apps.get_model('app_pdv', 'FormaPagamentoLoja')
    for loja in Loja.objects.all():
        for padrao in FORMAS_PAGAMENTO_PADRAO:
            FormaPagamentoLoja.objects.get_or_create(
                loja=loja,
                codigo=padrao['codigo'],
                defaults={
                    'nome': padrao['nome'],
                    'cor': padrao['cor'],
                    'icone': padrao['icone'],
                    'ordem': padrao['ordem'],
                    'eh_sistema': True,
                    'ativo': True,
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0027_loja_usa_moveon'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormaPagamentoLoja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, verbose_name='Nome exibido')),
                ('codigo', models.SlugField(max_length=30, verbose_name='Código interno')),
                ('cor', models.CharField(default='#9c27b0', max_length=7, verbose_name='Cor (hex)')),
                ('icone', models.CharField(default='fa-wallet', max_length=50, verbose_name='Ícone FontAwesome')),
                ('eh_sistema', models.BooleanField(default=False, verbose_name='Forma padrão do sistema?')),
                ('ativo', models.BooleanField(default=True)),
                ('ordem', models.PositiveIntegerField(default=0)),
                ('loja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='formas_pagamento', to='app_pdv.loja')),
            ],
            options={
                'verbose_name': 'Forma de Pagamento',
                'verbose_name_plural': 'Formas de Pagamento',
                'ordering': ['ordem', 'nome'],
                'unique_together': {('loja', 'codigo')},
            },
        ),
        migrations.AlterField(
            model_name='venda',
            name='forma_pagamento',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Forma de Pagamento'),
        ),
        migrations.AlterField(
            model_name='transacao',
            name='forma_pagamento',
            field=models.CharField(default='DINHEIRO', max_length=30, verbose_name='Forma de Pagamento'),
        ),
        migrations.RunPython(criar_formas_padrao_existentes, migrations.RunPython.noop),
    ]
