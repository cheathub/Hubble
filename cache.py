import operator
from queue import Queue


def _fetch(url, token):
    from urllib.request import urlopen
    import json
    import time

    time.sleep(1)
    response = urlopen(url + '?access_token=' + token)
    data = response.read().decode("utf-8")
    return json.loads(data)


class MockUser:
    def __init__(self, _login, _id):
        self.login = _login
        self.id = _id


class MockRepo:
    def __init__(self, _owner, _id, _name):
        self.owner = _owner
        self.id = _id
        self.name = _name


class Cache:

    token = ""

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

    def markdown(self, log='./log.md'):
        log = open(log, 'w+')

        import collections

        print("# cheats\n", file=log)

        print("Cheats 是一个收集在 GitHub 上作弊用户的黑名单项目。欢迎提交 Pull Request。", file=log)

        print("\n## 作弊用户\n", file=log)

        for uid, user in collections.OrderedDict(sorted(self.__cheat_user_list.items())).items():
            print("[" + user.login + "](https://github.com/" + user.login + ") " + " id: " + str(user.id) + "\n",
                  file=log)

        print("\n## 作弊仓库\n", file=log)
        for repo in sorted(
                self.__cheat_repo_list.values(),
                key=operator.attrgetter('owner.id', 'id')
        ):
            owner = self.__cheat_user_list[repo.owner.id]
            print(
                "[" + owner.login + "/" + repo.name + "](https://github.com/" +
                owner.login + "/" + repo.name + ") " + " id: " +
                str(owner.id) + "/" + str(repo.id) + "\n", file=log)

        print("\n## 假用户名单\n", file=log)
        for uid, user in collections.OrderedDict(sorted(self.__fake_user_list.items())).items():
            print("[" + user.login + "](https://github.com/" + user.login + ") " + " id: " + str(user.id) + "\n",
                  file=log)

    def load_markdown(self):

        options_parse = {
            0: self.__parse_none,
            1: self.__parse_cheat_user,
            2: self.__parse_cheat_repo,
            3: self.__parse_fake_user
        }

        with open('./log.md', 'r') as ins:
            option = 0
            for line in filter(None, (line.rstrip() for line in ins)):
                if '##' in line:
                    option += 1
                    continue
                options_parse[option](line)

    def __parse_none(self, line):
        pass

    def __parse_cheat_user(self, line):
        import re
        login = re.findall(r'\[(.*)\]', line)[0]
        uid = int(re.findall(r'id: (.*)', line)[0])
        self.__cheat_user_list[uid] = MockUser(login, uid)

    def __parse_cheat_repo(self, line):
        import re
        s1 = re.findall(r'\[(.*)/(.*)\]', line)[0]
        s2 = re.findall(r'id: (.*)/(.*)', line)[0]
        login = s1[0]
        repo = s1[1]
        uid = int(s2[0])
        rid = int(s2[1])
        self.__cheat_repo_list[rid] = MockRepo(MockUser(login, uid), rid, repo)

    def __parse_fake_user(self, line):
        import re
        login = re.findall(r'\[(.*)\]', line)[0]
        uid = int(re.findall(r'id: (.*)', line)[0])
        self.__fake_user_list[uid] = MockUser(login, uid)

    def recheck(self):
        for uid, user in self.__cheat_user_list.items():
            u = _fetch('https://api.github.com/user/' + str(uid), self.token)
            if user.login != u['login']:
                print(user.login, '-->', u['login'])
                self.__cheat_user_list[uid] = MockUser(u['login'], uid)

        for uid, user in self.__fake_user_list.items():
            u = _fetch('https://api.github.com/user/' + str(uid), self.token)
            if user.login != u['login']:
                print(user.login, '-->', u['login'])
                self.__fake_user_list[uid] = MockUser(u['login'], uid)

        for rid, repo in self.__cheat_repo_list.items():
            r = _fetch('https://api.github.com/repositories/' + str(rid), self.token)
            if repo.name != r['name']:
                print(repo.name, '-->', r['name'])
                self.__cheat_repo_list[rid] = MockRepo(
                    self.__cheat_user_list[repo.owner.id],
                    rid,
                    r['name']
                )

cache = Cache()


