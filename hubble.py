import datetime
from github import Github

bait = 'filelife'

g = Github('YOUR_GITHUB_TOKEN')

cheat_users = dict()
cheat_repos = dict()
fake_users = dict()
fake_stars = dict()

date = datetime.datetime(2017, 1, 1)
log = open('./log.txt', 'w+')


def analyze(repo):
    try:
        # ignore if repo is in list or repo's start is higher than 500
        if repo.id in cheat_repos or repo.stargazers_count >= 500:
            return
        # save repo's owner to cheat user list
        cheat_users[repo.owner.id] = repo.owner
        # ignore repo's with star less than 10
        if repo.stargazers_count >= 10:
            # save repo to cheat repo list
            cheat_repos[repo.id] = repo
            # continue count
            c_count = 0
            # pass count
            p_count = 0
            # loop repo's stargazers
            for stargazer in repo.get_stargazers():
                # ignore if stargazer is in fake user list
                if stargazer.id not in fake_users:
                    # ignore if stargazer have 10 public repo, or created date older than 20170101, or has no name,
                    # or has no bio
                    if stargazer.public_repos > 10 \
                            or stargazer.created_at < date \
                            or not stargazer.name \
                            or not stargazer.bio:
                        c_count += 1
                        continue

                    # stop if continue count is far greater than pass count and remove from cheat repo list
                    if p_count <= 10 and c_count - p_count > 20:
                        del cheat_repos[repo.id]
                        break

                    # save stargazer to fake user list
                    fake_users[stargazer.id] = stargazer

                    # get fake user's star repo and loop
                    starred = stargazer.get_starred()
                    for s_r in starred:
                        # ignore if repo is in fake star list or repo type is not user
                        if s_r.id not in fake_stars \
                                and s_r.owner.type == 'User':
                            # save repo to fake star repo list
                            fake_stars[s_r.id] = s_r
                            print(s_r.id, s_r.owner.login, s_r.name)
                            # recursive analyze fake repo
                            analyze(s_r)
                            p_count += 1
                        else:
                            pass
    except Exception as e:
        print(e, file=log)


for r in g.get_user(bait).get_repos():
    analyze(r)

print('------------cheat users------------', file=log)

for uid, user in cheat_users.items():
    print(uid, user.login, file=log)

print('------------cheat repos------------', file=log)

for rid, r in cheat_repos.items():
    print(rid, r.owner.login + '/' + r.name, r.stargazers_count, file=log)

print('------------fake users------------', file=log)

for uid, user in fake_users.items():
    print(uid, user.login, file=log)

print('------------fake stars------------', file=log)

for sid, r in fake_stars.items():
    print(sid, r.owner.login, r.name, file=log)

