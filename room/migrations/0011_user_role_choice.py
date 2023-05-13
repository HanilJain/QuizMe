# Generated by Django 4.2 on 2023-05-12 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('room', '0010_alter_questions_question_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role_choice',
            field=models.CharField(choices=[('QuizTaker', 'QuizTaker'), ('QuizMaster', 'QuizMaster')], default='QuizTaker', max_length=20),
        ),
    ]
