# Generated by Django 5.1.7 on 2025-03-31 13:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokcs', '0006_userdailyquiz_total_score'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectiveGrading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_keywords_matched', models.TextField(blank=True, help_text='자동 채점 시 매칭된 키워드')),
                ('auto_keywords_missed', models.TextField(blank=True, help_text='자동 채점 시 누락된 키워드')),
                ('auto_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('manually_corrected', models.BooleanField(default=False)),
                ('manual_score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('corrected_at', models.DateTimeField(blank=True, null=True)),
                ('correction_memo', models.TextField(blank=True)),
                ('answer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='grading', to='tokcs.subjectiveanswer')),
                ('corrected_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='manual_graders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
