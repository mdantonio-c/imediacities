"""
Test IMC endpoints
"""

from rapydo.services.authentication import BaseAuthentication as ba
from rapydo.tests.utilities import TestUtilities
# from rapydo.tests.utilities import (
#     OK, NO_CONTENT, PARTIAL, BAD_REQUEST, FORBIDDEN, NOTFOUND, CONFLICT
# )

from rapydo.utils.logs import get_logger
log = get_logger(__name__)

__author__ = "Mattia D'Antonio (m.dantonio@cineca.it)"


class TestTelethon(TestUtilities):

    def test_00_save_definitions(self):
        self.save("specs", self.get_specs())

        self.save_definition('admin/users', "def.users")
        self.save_definition('admin/users/{user_id}', "def.user")

        self.save_definition('admin/groups', "def.groups")
        self.save_definition('admin/groups/{group_id}', "def.group")

    def test_01_login(self):

        # Auth init from base/custom config
        ba.myinit()
        admin_headers, admin_token = self.do_login(
            ba.default_user, ba.default_password)

        self.save("admin_headers", admin_headers)
        self.save("admin_token", admin_token)

        admin_profile = self.get_profile(admin_headers)
        self.assertIn("admin_root", admin_profile["roles"])
        self.save("admin_profile", admin_profile)

    # def test_02_create_environment(self):

    #     admin_headers = self.get("admin_headers")
    #     admin_profile = self.get("admin_profile")

    #     users_def = self.get("def.users")
    #     user_def = self.get("def.user")
    #     groups_def = self.get("def.groups")
    #     group_def = self.get("def.group")

    def test_34_modify_users_groups(self):
        admin_headers = self.get("admin_headers")

        # NOT USED, JUST TO TEST THE ENDPOINT
        self.getDynamicInputSchema('admin/groups', admin_headers)

        # group1 = self.get("group1")
        # user1 = self.get("user1")
        # profile = self.get("profile")

        # user_def = self.get("def.user")
        # group_def = self.get("def.group")

        # data = {}
        # data['fullname'] = "A new name"
        # data['pi'] = profile['uuid']
        # self._test_update(
        #     group_def, 'admin/groups/' + group1,
        #     admin_headers, data, NO_CONTENT)

        # data = {}
        # data['name'] = "A new name"
        # data['password'] = self.randomString()
        # data['group'] = group1
        # self._test_update(
        #     user_def, 'admin/users/' + user1,
        #     admin_headers, data, NO_CONTENT)

    def test_35_delete_users_groups_institutes(self):

        # admin_headers = self.get("admin_headers")

        # group1 = self.get("group1")
        # group2 = self.get("group2")
        # user1 = self.get("user1")
        # user2 = self.get("user2")
        # user3 = self.get("user3")
        # user_def = self.get("def.user")
        # group_def = self.get("def.group")

        # self._test_delete(
        #     user_def, 'admin/users/' + user1,
        #     admin_headers, NO_CONTENT)
        # self._test_delete(
        #     user_def, 'admin/users/' + user2,
        #     admin_headers, NO_CONTENT)
        # self._test_delete(
        #     user_def, 'admin/users/' + user3,
        #     admin_headers, NO_CONTENT)

        # self._test_delete(
        #     group_def, 'admin/groups/' + group1,
        #     admin_headers, NO_CONTENT)
        # self._test_delete(
        #     group_def, 'admin/groups/' + group2,
        #     admin_headers, NO_CONTENT)
        pass

    def test_36_destroy_tokens(self):

        self.destroyToken(self.get("admin_token"), self.get("admin_headers"))
        # These users have been deleted, cannot destroy tokens
        # self.destroyToken(self.get("token"), self.get("headers"))
        # self.destroyToken(self.get("token2"), self.get("headers2"))
        # self.destroyToken(self.get("token3"), self.get("headers3"))
