from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0015_certificates_delete_certificate'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCertificate',
            fields=[
                ('id', models.BigAutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('date_of_completion', models.DateField(auto_now_add=True)),
                ('pdf_files', models.FileField(blank=True, null=True, upload_to='certificates/')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.userregister')),
            ],
            options={
                'unique_together': {('user', 'course')},
            },
        ),
        # Replace DeleteModel with a DROP TABLE IF EXISTS
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS myapp_certificates;",
            reverse_sql=migrations.RunSQL.noop
        ),
    ]
