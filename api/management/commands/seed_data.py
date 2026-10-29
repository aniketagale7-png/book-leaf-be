"""
Django Management Command: seed_data
Alias for seed_sample_data command to ensure both commands work seamlessly.
"""

from django.core.management.base import BaseCommand
from api.management.commands.seed_sample_data import Command as SampleDataCommand

class Command(BaseCommand):
    help = 'Seeds official BookLeaf assignment dataset (Alias for seed_sample_data)'

    def handle(self, *args, **kwargs):
        SampleDataCommand().handle(*args, **kwargs)
