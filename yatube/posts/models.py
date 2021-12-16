from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Community model."""
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('group name', unique=True)
    description = models.TextField('description')

    class Meta:
        verbose_name = 'community'
        db_table = 'community of Tolstoy lovers'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Model for records, field group is linked by model
    Group and author is linked by User."""
    text = models.TextField('article', help_text='Введите текст поста')
    pub_date = models.DateTimeField('year of writing', auto_now_add=True)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='group name',
        related_name='community',
        help_text='Выберите группу',
        blank=True,
        null=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author',
        related_name='author_posts')
    image = models.ImageField(
        'beautiful image',
        upload_to='posts/',
        blank=True,
        help_text='Загрузить картинку'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'notes of famous people'
        db_table = 'all post'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Add commets to post."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='post name',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='author name',
        related_name='author_comments')
    text = models.TextField('coment', help_text='Введите текст коментария')
    created = models.DateTimeField('time of writing', auto_now_add=True)

    class Meta:
        verbose_name = 'comments'
        db_table = 'users comments'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """Subscribe to the author."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='name',
        related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='post author',
        related_name='following')

    class Meta:
        verbose_name = 'subscriptions'
        db_table = 'author subscriptions'
        unique_together = ['user', 'author']

    def __str__(self):
        return f'{self.user} subscribed to {self.author}'

    def save(self, *args, **kwargs):
        in_base = Follow.objects.filter(user=self.user,
                                        author=self.author).count()
        if self.user == self.author or in_base:
            return
        else:
            super().save(*args, **kwargs)
