from django.db import models

class Character(models.Model):
    rank = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    series = models.CharField(max_length=200)
    value = models.CharField(max_length=20)  # e.g., "170 ka"
    note = models.TextField(blank=True)
    image = models.CharField(max_length=500, blank=True)  # Path to image
    sort_order = models.IntegerField(default=0)  # To maintain original JSON order
    in_trade_list = models.BooleanField(default=False)  # For tracking trade list status
    
    def __str__(self):
        return f"{self.name} ({self.series})"
        
    class Meta:
        ordering = ['sort_order']