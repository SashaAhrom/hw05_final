from django.test import Client, TestCase
from django.urls import reverse


class AboutViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_tech_correct_namespase_name(self):
        """The template uses the correct namespase:name."""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
