from django.db import models

# Create your models here.
class Quote(models.Model):
    text = models.TextField(verbose_name="Цитата")
    source = models.CharField(max_length=200, verbose_name="Источник (фильм, книга и т.п.)")
    weight = models.PositiveIntegerField(default=1, verbose_name="Вес (чем выше — тем чаще)")
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"

    def __str__(self):
        return f"{self.text[:50]}... ({self.source})"

class Vote(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255)  # можно заменить на cookie_id
    vote_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quote', 'session_id')  # один пользователь — один голос
        verbose_name = "Голос"
        verbose_name_plural = "Голоса"

    def __str__(self):
        return f"{self.session_id} → {self.quote.text[:30]} ({self.vote_type})"