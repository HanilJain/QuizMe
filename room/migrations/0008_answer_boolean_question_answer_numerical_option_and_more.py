# Generated by Django 4.2 on 2023-05-09 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0007_remove_user_role_choice'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='boolean_question',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='answer',
            name='numerical_option',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='questions',
            name='question_type',
            field=models.CharField(choices=[('numerical', 'numerical'), ('Boolean', 'Boolean'), ('mcq', 'mcq')], default='mcq', max_length=10),
        ),
    ]
