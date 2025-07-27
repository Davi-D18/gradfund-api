from django.db import models

class SeederExecution(models.Model):
    app_label = models.CharField(max_length=100)
    seeder_name = models.CharField(max_length=100)
    executed_at = models.DateTimeField(auto_now_add=True)
    data_hash = models.CharField(max_length=64, blank=True, null=True)
    
    class Meta:
        unique_together = ('app_label', 'seeder_name')
        verbose_name = 'Seeder Execution'
        verbose_name_plural = 'Seeder Executions'
    
    def __str__(self):
        return f"{self.app_label}.{self.seeder_name} - {self.executed_at}"