import unittest

from policy_maker import app


class TestGetPrincipalTag(unittest.TestCase):

  def test_tag_present(self):
    tags = [
      {'Key': 'heresatag', 'Value': 'heresatagvalue'},
      {'Key': 'theresatag', 'Value': 'theresatagvalue'},
      {'Key': 'aws:servicecatalog:provisioningPrincipalArn', 'Value': 'foo/bar'}
    ]
    result = app.get_principal_tag(tags)
    self.assertEqual(result, 'foo/bar')

  def test_tag_missing(self):
    with self.assertRaises(ValueError):
      tags = [
        {'Key': 'heresatag', 'Value': 'heresatagvalue'},
        {'Key': 'theresatag', 'Value': 'theresatagvalue'}
      ]
      app.get_principal_tag(tags)
