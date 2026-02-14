from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    real_name = models.CharField('실명', max_length=30)

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자'

    def __str__(self):
        return f'{self.real_name} ({self.username})'


class WorshipRecord(models.Model):
    class WorshipType(models.TextChoices):
        FAMILY = 'family', '가정예배'
        PERSONAL = 'personal', '개인예배'
        DAWN = 'dawn', '새벽예배'
        OTHER = 'other', '기타'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worship_records')
    date = models.DateField('예배 날짜')
    worship_type = models.CharField('예배 종류', max_length=20, choices=WorshipType.choices, default=WorshipType.FAMILY)
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용', blank=True)
    is_shared = models.BooleanField('게시판 공유', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '예배 기록'
        verbose_name_plural = '예배 기록'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.date} - {self.title}'

    @property
    def like_count(self):
        return self.likes.count()


class Comment(models.Model):
    record = models.ForeignKey(WorshipRecord, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField('댓글')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.real_name}: {self.content[:30]}'


class Like(models.Model):
    record = models.ForeignKey(WorshipRecord, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '좋아요'
        verbose_name_plural = '좋아요'
        unique_together = ('record', 'user')

    def __str__(self):
        return f'{self.user.real_name} -> {self.record.title}'
