from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_pdv', '0028_formapagamentoloja'),
    ]

    operations = [
        migrations.AddField(
            model_name='loja',
            name='monitorar_entrega',
            field=models.BooleanField(
                default=True,
                help_text='Sim: fluxo normal com app do motoboy (Em Separação → Em Rota → Finalizado). Não: finaliza direto pela Torre de Controle, sem precisar do app.',
                verbose_name='Monitorar Entrega?',
            ),
        ),
    ]
