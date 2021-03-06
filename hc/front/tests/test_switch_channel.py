from hc.api.models import Channel, Check
from hc.test import BaseTestCase


class SwitchChannelTestCase(BaseTestCase):

    def setUp(self):
        super(SwitchChannelTestCase, self).setUp()
        self.check = Check(user=self.alice)
        self.check.save()

        self.channel = Channel(user=self.alice, kind="email")
        self.channel.value = "alice@example.org"
        self.channel.save()

        self.url = "/checks/%s/channels/%s/enabled" % (self.check.code, self.channel.code)

    def test_it_enables(self):
        self.client.login(username="alice@example.org", password="password")
        self.client.post(self.url, {"state": "on"})

        self.assertTrue(self.channel in self.check.channel_set.all())

    def test_it_disables(self):
        self.check.channel_set.add(self.channel)

        self.client.login(username="alice@example.org", password="password")
        self.client.post(self.url, {"state": "off"})

        self.assertFalse(self.channel in self.check.channel_set.all())

    def test_it_checks_ownership(self):
        self.client.login(username="charlie@example.org", password="password")
        r = self.client.post(self.url, {"state": "on"})
        self.assertEqual(r.status_code, 403)

    def test_it_checks_channels_ownership(self):
        cc = Check(user=self.charlie)
        cc.save()

        # Charlie will try to assign Alice's channel to his check:
        self.url = "/checks/%s/channels/%s/enabled" % (cc.code, self.channel.code)

        self.client.login(username="charlie@example.org", password="password")
        r = self.client.post(self.url, {"state": "on"})
        self.assertEqual(r.status_code, 403)
