# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-06-20 12:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('due_date', models.DateField()),
                ('ass_date', models.DateField()),
                ('ass_type', models.CharField(max_length=255)),
                ('ass_name', models.CharField(max_length=255)),
                ('description', models.CharField(default='', max_length=255)),
                ('ass_number', models.IntegerField(default=1)),
                ('closed', models.BooleanField(default=False)),
                ('slug', models.CharField(default='', max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='No Course Title Provided', max_length=255)),
                ('info', models.CharField(default='There is no Course Description', max_length=400)),
                ('term', models.CharField(choices=[('Winter', 'Winter'), ('Spring', 'Spring'), ('Summer', 'Summer'), ('Fall', 'Fall')], default='None', max_length=6)),
                ('disable', models.BooleanField(default=False)),
                ('slug', models.CharField(max_length=20, unique=True)),
                ('addCode', models.CharField(max_length=10, unique=True)),
                ('year', models.CharField(default=2019, max_length=20)),
                ('limit_creation', models.BooleanField(default=False)),
                ('limit_interest', models.BooleanField(default=False)),
                ('limit_weights', models.BooleanField(default=False)),
                ('weigh_interest', models.IntegerField(default=1)),
                ('weigh_know', models.IntegerField(default=1)),
                ('weigh_learn', models.IntegerField(default=1)),
                ('csv_file', models.FileField(default='', upload_to='csv_files/')),
                ('assignments', models.ManyToManyField(related_name='course', to='courses.Assignment')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
            },
        ),
        migrations.CreateModel(
            name='CourseUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='No Title Provided', max_length=255)),
                ('content', models.TextField(default='*No Content Provided*', max_length=2000)),
                ('date_post', models.DateTimeField()),
                ('date_edit', models.DateTimeField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course Update',
                'verbose_name_plural': 'Course Updates',
                'ordering': ('-date_post', '-date_edit', 'title'),
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='student', max_length=24)),
                ('course', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='courses.Course')),
                ('user', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='enrollmentUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
