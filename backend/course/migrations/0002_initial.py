# Generated by Django 4.2 on 2025-05-25 22:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lessonprogress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='chapter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='course.chapter', verbose_name='فصل'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='course.course', verbose_name='دوره'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='discount_used',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='course.discount', verbose_name='تخفیف استفاده شده'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AddField(
            model_name='discount',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to='course.course', verbose_name='دوره'),
        ),
        migrations.AddField(
            model_name='courserating',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='course.course', verbose_name='دوره'),
        ),
        migrations.AddField(
            model_name='courserating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_ratings', to=settings.AUTH_USER_MODEL, verbose_name='کاربر'),
        ),
        migrations.AddField(
            model_name='course',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL, verbose_name='مدرس'),
        ),
        migrations.AddField(
            model_name='course',
            name='prerequisites',
            field=models.ManyToManyField(blank=True, related_name='required_for', to='course.course', verbose_name='پیش\u200cنیازها'),
        ),
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='courses', to='course.tag', verbose_name='برچسب\u200cها'),
        ),
        migrations.AddField(
            model_name='chapter',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chapters', to='course.course', verbose_name='دوره'),
        ),
        migrations.AddIndex(
            model_name='lessonprogress',
            index=models.Index(fields=['user', 'lesson', 'is_completed'], name='course_less_user_id_cf104f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='lessonprogress',
            unique_together={('user', 'lesson')},
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('chapter', 'order')},
        ),
        migrations.AddIndex(
            model_name='enrollment',
            index=models.Index(fields=['user', 'course', 'status'], name='course_enro_user_id_aa3ae9_idx'),
        ),
        migrations.AddIndex(
            model_name='enrollment',
            index=models.Index(fields=['created_at'], name='course_enro_created_732b72_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('user', 'course')},
        ),
        migrations.AddIndex(
            model_name='discount',
            index=models.Index(fields=['code', 'is_active'], name='course_disc_code_cd7e7d_idx'),
        ),
        migrations.AddIndex(
            model_name='discount',
            index=models.Index(fields=['start_date', 'end_date'], name='course_disc_start_d_c2b112_idx'),
        ),
        migrations.AddIndex(
            model_name='courserating',
            index=models.Index(fields=['course', 'rating'], name='course_cour_course__89a228_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='courserating',
            unique_together={('course', 'user')},
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['status', 'level'], name='course_cour_status_88e14b_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['created_at'], name='course_cour_created_49f06e_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='chapter',
            unique_together={('course', 'order')},
        ),
    ]
