from queue import Queue


class Cache:
    __fake_user_list = dict()
    __real_user_list = dict()

    __cheat_user_list = dict()
    __cheat_repo_list = dict()

    __tracking_user_pool = Queue()
    __tracking_repo_pool = Queue()

    __fake_starred_repos = dict()

    def track_repo(self, repo):
        self.__tracking_repo_pool.put(repo)
        self.__fake_starred_repos[repo.id] = repo

    def track_user(self, user):
        self.__tracking_user_pool.put(user)

    def tag_cheat_user(self, user):
        self.__cheat_user_list[user.id] = user

    def tag_cheat_repo(self, repo):
        self.__cheat_repo_list[repo.id] = repo

    def empty(self):
        return self.__tracking_repo_pool.empty()

    def user_empty(self):
        return self.__tracking_user_pool.empty()

    def pop_repo(self):
        if self.empty():
            return None
        return self.__tracking_repo_pool.get()

    def pop_user(self):
        if self.user_empty():
            return None
        return self.__tracking_user_pool.get()

    def has_repo(self, rid):
        return rid in self.__fake_starred_repos

    def has_fake_user(self, uid):
        return uid in self.__fake_user_list

    def has_real_user(self, uid):
        return uid in self.__real_user_list

    def tag_fake_user(self, user):
        self.__fake_user_list[user.id] = user

    def tag_real_user(self, user):
        self.__real_user_list[user.id] = user

    def get_real_user(self, uid):
        return self.__real_user_list[uid]

    def get_fake_user(self, uid):
        return self.__fake_user_list[uid]

    def get_user_info(self, uid):

        if self.has_real_user(uid):
            user = self.get_real_user(uid)
            return user.reason, user.starred_repositories, user.forked_repositories
        if self.has_fake_user(uid):
            user = self.get_fake_user(uid)
            return user.reason, user.starred_repositories, user.forked_repositories
        return "none", dict(), dict()

    def markdown(self):
        log = open('./log.md', 'w+')

        print("\n## cheat user\n", file=log)
        for uid, user in self.__cheat_user_list.items():
            print("[" + user.login + "](https://github.com/" + user.login + ") " + " id: " + str(user.id) + "\n",
                  file=log)

        print("\n## cheat repo\n", file=log)
        for rid, repo in self.__cheat_repo_list.items():
            print(
                "[" + repo.owner.login + "/" + repo.name + "](https://github.com/" +
                repo.owner.login + "/" + repo.name + ") " + " id: " +
                str(repo.owner.id) + "/" + str(repo.id) + "\n", file=log)

        print("\n## fake user\n", file=log)
        for uid, user in self.__fake_user_list.items():
            print("[" + user.login + "](https://github.com/" + user.login + ") " + " id: " + str(user.id) + "\n",
                  file=log)


cache = Cache()
