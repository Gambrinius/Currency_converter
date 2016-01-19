from django.db import models

# Create your models here.


class Currency(models.Model):
    class Meta:
        db_table = 'currency'
        ordering = ['base', 'rate']

    base = models.CharField(max_length=3)
    rate = models.CharField(max_length=3)
    value = models.FloatField()

    def __str__(self):              # return description string
        return '%s - %s' % (self.base, self.rate)


class FullName(models.Model):
    class Meta:
        db_table = 'fullname'
        ordering = ['symbols']

    symbols = models.CharField(max_length=3)
    name = models.CharField(max_length=200)

    def __str__(self):
        return '%s (%s)' % (self.symbols, self.name)
