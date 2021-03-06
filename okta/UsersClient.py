import json

from okta.framework.ApiClient import ApiClient
from okta.framework.Utils import Utils
from okta.framework.PagedResults import PagedResults
from okta.models.user.User import User
from okta.models.user.ActivationResponse import ActivationResponse
from okta.models.user.TempPassword import TempPassword
from okta.models.user.ResetPasswordToken import ResetPasswordToken
from okta.models.user.LoginCredentials import LoginCredentials
from okta.models.usergroup.UserGroup import UserGroup


class UsersClient(ApiClient):
    user_model = User

    def __init__(self, base_url, api_token):
        ApiClient.__init__(self, base_url + '/api/v1/users', api_token)

    # CRUD

    def get_users(self, limit=None, q=None, filter_string=None,
                  search_string=None):
        """Get a list of Users

        :param limit: maximum number of users to return
        :type limit: int or None
        :param q: string to search users' first names, last names, and emails
        :type q: str or None
        :param filter_string: string to filter users
        :type filter_string: str or None
        :param search_string: string to search users
        :type search_string: str or None
        :rtype: list of User
        """
        params = {
            'limit': limit,
            'q': q,
            'filter': filter_string,
            'search': search_string,
        }
        response = ApiClient.get_path(self, '/', params=params)
        return Utils.deserialize(response.text, self.user_model)

    def get_user(self, uid):
        """Get a single user

        :param uid: the user id or login
        :type uid: str
        :rtype: User
        """
        response = ApiClient.get_path(self, '/{0}'.format(uid))
        return Utils.deserialize(response.text, self.user_model)

    def get_user_groups(self, uid):
        """Get the groups a single user is a member of

        :param uid: the user id or login
        :type uid: str
        :rtype: list of UserGroup
        """
        response = ApiClient.get_path(self, '/{0}/groups'.format(uid))
        return Utils.deserialize(response.text, UserGroup)

    def get_user_apps(self, uid):
        """Get the apps a single user has access to

        :param uid: the user id or login
        :type uid: str
        :rtype: dict
        """
        response = ApiClient.get_path(self, '/{0}/appLinks'.format(uid))
        return json.loads(response.text)

    def update_user(self, user):
        """Update a user

        :param user: the user to update
        :type user: User
        :rtype: User
        """
        return self.update_user_by_id(user.id, user)

    def update_user_partially(self, user):
        """Partially update a user

        :param user: the user to update
        :type user: User
        :rtype: User
        """
        return self.update_user_by_id_partially(user.id, user)

    def update_user_by_id(self, uid, user):
        """Update a user, defined by an id

        :param uid: the target user id
        :type uid: str
        :param user: the data to update the target user
        :type user: User
        :rtype: User
        """
        response = ApiClient.put_path(self, '/{0}'.format(uid), user)
        return Utils.deserialize(response.text, self.user_model)

    def update_user_by_id_partially(self, uid, user):
        """Partially update a user, defined by an id

        :param uid: the target user id
        :type uid: str
        :param user: the data to update the target user
        :type user: User
        :rtype: User
        """
        response = ApiClient.post_path(self, '/{0}'.format(uid), user)
        return Utils.deserialize(response.text, self.user_model)

    def create_user(self, user, activate=False):
        """Create a user

        :param user: the data to create a user
        :type user: User
        :param activate: whether to activate the user
        :type activate: bool
        :rtype: User
        """
        if activate is None:
            response = ApiClient.post_path(self, '/', user)
        else:
            params = {
                'activate': activate
            }
            response = ApiClient.post_path(self, '/', user, params=params)
        return Utils.deserialize(response.text, self.user_model)

    def delete_user(self, uid):
        """Delete user by target id

        :param uid: the target user id
        :type uid: str
        :return: None
        """
        response = ApiClient.delete_path(self, '/{0}'.format(uid))
        return Utils.deserialize(response.text, self.user_model)

    def get_paged_users(self, limit=None, filter_string=None,
                        search_string=None, after=None, url=None):
        """Get a paged list of Users

        :param limit: maximum number of users to return
        :type limit: int or None
        :param filter_string: string to filter users
        :type filter_string: str or None
        :param search_string: string to search users
        :type search_string: str or None
        :param after: user id that filtering will resume after
        :type after: str
        :param url: url that returns a list of User
        :type url: str
        :rtype: PagedResults of User
        """
        if url:
            response = ApiClient.get(self, url)

        else:
            params = {
                'limit': limit,
                'after': after,
                'filter': filter_string,
                'search': search_string
            }
            response = ApiClient.get_path(self, '/', params=params)

        return PagedResults(response, self.user_model)

    # LIFECYCLE

    def activate_user(self, uid, send_email=True):
        """Activate user by target id

        :param uid: the target user id
        :type uid: str
        :param send_email: sends an activation email to the user
        :type send_email: bool
        :return: None or ActivationResponse
        """
        params = {
            'sendEmail': send_email,
        }
        response = ApiClient.post_path(self, '/{0}/lifecycle/activate'.format(uid), params=params)
        return Utils.deserialize(response.text, ActivationResponse)

    def deactivate_user(self, uid):
        """Deactivate user by target id

        :param uid: the target user id
        :type uid: str
        :return: empty User
        """
        response = ApiClient.post_path(self, '/{0}/lifecycle/deactivate'.format(uid))
        return Utils.deserialize(response.text, self.user_model)

    def unlock_user(self, uid):
        """Unlock user by target id

        :param uid: the target user id
        :type uid: str
        :return: User
        """
        response = ApiClient.post_path(self, '/{0}/lifecycle/unlock'.format(uid))
        return Utils.deserialize(response.text, self.user_model)

    def reset_password(self, uid, send_email=True):
        """Reset user's password by target user id

        :param uid: the target user id
        :type uid: str
        :param send_email: whether a password reset email should be sent
        :type send_email: bool
        :return: None or ResetPasswordToken
        """
        params = {
            'sendEmail': send_email
        }
        response = ApiClient.post_path(self, '/{0}/lifecycle/reset_password'.format(uid), params=params)
        return Utils.deserialize(response.text, ResetPasswordToken)

    def change_password(self, uid, old_password, new_password):
        """Change user's password by target user id

        :param uid: the target user id
        :type uid: str
        :param old_password: the user's old password
        :type old_password: str
        :param new_password: the desired new password
        :type new_password: str
        :return: None or LoginCredentials
        """
        data = {
            'oldPassword': {
                'value': old_password
            },
            'newPassword': {
                'value': new_password
            }
        }
        response = ApiClient.post_path(self, '/{0}/credentials/change_password'.format(uid), data)
        return Utils.deserialize(response.text, LoginCredentials)

    def expire_password(self, uid, temp_password=False):
        """Expire user's password by target user id

        :param uid: the target user id
        :type uid: str
        :param temp_password: whether a temporary password should be set
        :type temp_password: bool
        :return: None or TempPassword
        """
        if not temp_password:
            ApiClient.post_path(self, '/{0}/lifecycle/expire_password'.format(uid))
        else:
            params = {
                'tempPassword': temp_password
            }
            response = ApiClient.post_path(self, '/{0}/lifecycle/expire_password'.format(uid), params=params)
            return Utils.deserialize(response.text, TempPassword)
