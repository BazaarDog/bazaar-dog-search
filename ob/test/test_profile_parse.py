import json
import os

from django.db import transaction
from django.test.testcases import TestCase

from ob.models.profile import Profile
from ob.tasks.sync_profile import parse_profile


class ProfileTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_profile_parse(self):
        pwd = os.path.dirname(__file__)
        with open(pwd + '/data_responses/profile.json') as json_file:
            data = json.load(json_file)
            peer = "QmcUDmZK8PsPYWw5FRHKNZFjszm2K6e68BQSTpnJYUsML7"
            with transaction.atomic():
                p, p_c = Profile.objects.get_or_create(peerID=peer)
            parse_profile(p, data)
