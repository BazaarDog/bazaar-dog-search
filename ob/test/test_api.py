from django.test import Client

HTTP_USER_AGENT = 'OpenBazaar'

web_client = Client()
response = web_client.get('/')
