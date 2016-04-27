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


class LastUpdateTable(models.Model):
    class Meta:
        db_table = 'last_update_table'

    SET_TABLES = (
        (Currency._meta.db_table, 'Currency Table'),
        (FullName._meta.verbose_name_plural, 'FullName Table'),
    )
    table_name = models.CharField(max_length=100, choices=SET_TABLES)
    datatime = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.table_name
