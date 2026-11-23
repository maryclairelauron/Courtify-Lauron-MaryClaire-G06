from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Court(models.Model):
    class Environment(models.TextChoices):
        INDOOR = 'indoor', 'Indoor'
        OUTDOOR = 'outdoor', 'Outdoor'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Available'
        MAINTENANCE = 'maintenance', 'Maintenance'

    name = models.CharField(max_length=50, unique=True)
    environment = models.CharField(max_length=10, choices=Environment.choices, default=Environment.INDOOR)
    rate_per_hour = models.DecimalField(max_digits=8, decimal_places=2,
                                        validators=[MinValueValidator(Decimal('1'))])
    max_players = models.PositiveSmallIntegerField(default=4,
                                                   validators=[MinValueValidator(1), MaxValueValidator(20)])
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name