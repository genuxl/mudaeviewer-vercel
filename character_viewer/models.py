from django.db import models
from django.contrib.auth.models import User

class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters', null=True, blank=True)
    rank = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    series = models.CharField(max_length=200, blank=True)  # Make it optional
    value = models.CharField(max_length=20)  # e.g., "170 ka"
    note = models.TextField(blank=True)
    image = models.TextField(blank=True)  # URL to external image
    sort_order = models.IntegerField(default=0)  # To maintain original JSON order
    in_trade_list = models.BooleanField(default=False)  # For tracking trade list status
    keys = models.IntegerField(default=0)  # Number of keys for the character
    key_type = models.CharField(max_length=10, blank=True)  # Type of key (bronze, silver, gold, chaos)
    
    def __str__(self):
        return f"{self.name} ({self.series})" if self.series else f"{self.name}"
        
    class Meta:
        ordering = ['sort_order']