from io import StringIO
import requests

from django.core.management import call_command
from django.test import TestCase
from ob.test.util import json2obj
from ob.util import update_price_values


class ClosepollTest(TestCase):
    fixtures = ['datadump.json']


    def test_command_output(self):
        out = StringIO()
        ob1_url = 'https://search.ob1.io/verified_moderators'
        call_command(
            "verified",
            url=ob1_url,
            stdout=out
        )
        response = requests.get('https://search.ob1.io/verified_moderators')
        r_obj = json2obj(response.content)
        num_moderators = len(r_obj.moderators)
        self.assertIn(
            "Updated {} verified vendors from {}".format(
                num_moderators,
                'https://search.ob1.io/verified_moderators'
            ),
            out.getvalue()
        )
