import unittest

from policy_maker import app

class TestAttachPolicy(unittest.TestCase):

  def test_one_principal(self):
    principal = 'a_principal'
    extras = None
    result = app.combine_principals(
      principal=principal,
      extra_principals=extras)
    self.assertCountEqual(result, [principal])

  def test_extra_principals(self):
    principal = 'a_principal'
    extras = ['foo', 'bar', 'baz']
    result = app.combine_principals(
      principal=principal,
      extra_principals=extras)
    expected = [principal, 'foo', 'bar', 'baz']
    self.assertCountEqual(result, expected)
