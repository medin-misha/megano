# Generated by Django 5.0.1 on 2024-02-28 07:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_alter_order_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='api.productimage')),
            ],
        ),
        migrations.CreateModel(
            name='SubCatigory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='api.catalogitem')),
                ('image', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subitem', to='api.productimage')),
            ],
        ),
    ]
