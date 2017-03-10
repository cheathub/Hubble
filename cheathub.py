from github import Github
from github import GithubObject
from github import AuthenticatedUser
from user import User


class CheatHub(Github):

    def get_user(self, login=GithubObject.NotSet):
        assert login is GithubObject.NotSet or isinstance(login, str), login
        if login is GithubObject.NotSet:
            return AuthenticatedUser.AuthenticatedUser(self._Github__requester, {}, {"url": "/user"}, completed=False)
        else:
            headers, data = self._Github__requester.requestJsonAndCheck(
                "GET",
                "/users/" + login
            )
            return User(self._Github__requester, headers, data, completed=True)
