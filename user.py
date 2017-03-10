from github.NamedUser import NamedUser
from github import GithubObject
from github import PaginatedList

import datetime
import repo


date = datetime.datetime(2017, 1, 1)


def enum(**enums):
    return type('Enum', (), enums)

Reasons = enum(
    NONE="none",
    FAKE="stars without repo",
    OLDER="older account",
    EMPTY="empty",
    STAR="starred same account",
    REPO="repo greater than fork"
)


class User(NamedUser):

    def __init__(self, requester, headers, attributes, completed):
        super().__init__(requester, headers, attributes, completed)
        self.starred_repositories = dict()
        self.forked_repositories = dict()
        self.starred_owner_count = dict()
        self.reason = Reasons.NONE

    def get_repos(self, type=GithubObject.NotSet):
        assert type is GithubObject.NotSet or isinstance(type, str), type
        url_parameters = dict()
        if type is not GithubObject.NotSet:
            url_parameters["type"] = type
        return PaginatedList.PaginatedList(
            repo.Repo,
            self._requester,
            self.url + "/repos",
            url_parameters
        )

    def get_starred(self):
        return PaginatedList.PaginatedList(
            repo.Repo,
            self._requester,
            self.url + "/starred",
            None
        )

    def is_real(self):

        while True:
            # real users' created date older than 20170101, or has no name, or has no bio
            #if self.created_at < date:
            if self.id < 25000000:
                self.reason = Reasons.OLDER
                break

            for s_r in self.get_repos():
                self.forked_repositories[s_r.id] = s_r

            starred_repo_list = self.get_starred()

            for s_s in starred_repo_list:
                self.starred_repositories[s_s.id] = s_s
                if s_s.owner.id not in self.starred_owner_count:
                    self.starred_owner_count[s_s.owner.id] = 0
                self.starred_owner_count[s_s.owner.id] += 1

            o_count = 0
            for oid, count in self.starred_owner_count.items():
                if count > 3:
                    o_count += 1

            if o_count > 1:
                self.reason = Reasons.STAR
                return False

            if self.created_at >= date \
                    and not self.name \
                    and not self.location \
                    and not self.bio \
                    and not self.company \
                    and len(self.starred_repositories) < 5:
                self.reason = Reasons.EMPTY
                break
            # fake users' repo is mostly forks
            fork_count = 0
            for s_id, s_r in self.forked_repositories.items():
                if s_r.fork:
                    fork_count += 1
            if self.public_repos - fork_count > 5:
                self.reason = Reasons.REPO
                break

            self.reason = Reasons.FAKE
            # we can assume the stargazer is a fake user and cache stargazer in fake user list
            return False

        return True
