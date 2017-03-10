from github.Repository import Repository
from github.PaginatedList import PaginatedList
import time
import user

from cache import cache


def enum(**enums):
    return type('Enum', (), enums)

Reasons = enum(
    NONE="none",
    ASSUMED="stars too less or too great",
    REAL="real star is greater than fake ones",
    FAKE="fake star is greater than real ones"
)


class Repo(Repository):

    def __init__(self, requester, headers, attributes, completed):
        super().__init__(requester, headers, attributes, completed)
        self.real_count = 0
        self.fake_count = 0
        self.stargazer_list = dict()
        self.reason = Reasons.NONE

    def get_stargazers(self):
        return PaginatedList(
            user.User,
            self._requester,
            self.url + "/stargazers",
            None
        )

    def __assumed_real_repo(self):
        if self.stargazers_count < 10 or self.stargazers_count > 500:
            # repo is too large or too small
            print(self.id, self.owner.login, self.name, "is OK, continue.")
            return True
        print(self.id, self.owner.login, self.name, "stars:", self.stargazers_count)
        return False

    def is_cheating(self):

        time.sleep(1)

        # api error count
        e_count = 0
        while e_count <= 60:
            try:
                if self.__assumed_real_repo():
                    self.reason = Reasons.ASSUMED
                    break

                for s in self.get_stargazers():

                    self.stargazer_list[s.id] = s

                    # we can assume this repo is not cheating if real star is far greater than fake ones.
                    if self.real_count - self.fake_count > 20:
                        self.reason = Reasons.REAL
                        break

                    if cache.has_real_user(s.id):
                        s.reason, s.starred_repositories, s.forked_repositories \
                            = cache.get_user_info(s.id)
                        self.real_count += 1
                        continue

                    if cache.has_fake_user(s.id):
                        s.reason, s.starred_repositories, s.forked_repositories \
                            = cache.get_user_info(s.id)
                        self.fake_count += 1
                        continue

                    time.sleep(1)

                    if s.is_real():
                        self.real_count += 1
                        print(s.id, s.login, s.name, '-> real: ' + s.reason)
                        cache.tag_real_user(s)
                    else:
                        print(s.id, s.login, s.name, '-> fake: ' + s.reason)
                        cache.tag_fake_user(s)
                        # add stargazer to tracking queue
                        cache.track_user(s)
                        self.fake_count += 1

                # we can assume the repo is cheating if fake count is far greater than real count
                if self.fake_count - self.real_count > 10 or self.fake_count >= self.stargazers_count / 4:
                    self.reason = Reasons.FAKE
                    return True
            except Exception as e:
                print(e)
                e_count += 1
                time.sleep(5 * e_count)
            return False
