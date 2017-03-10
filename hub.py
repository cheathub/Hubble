import argparse
from cache import cache
from cheathub import CheatHub

#g = CheatHub('YOUR_GITHUB_TOKEN')
g = CheatHub()


def track_user(stargazer):
    starred_repo_list = stargazer.get_starred()
    for s_r in starred_repo_list:
        if cache.has_repo(s_r.id) or s_r.owner.type != 'User':
            continue
        cache.track_repo(s_r)


def track(bait):
    for repo in g.get_user(bait).get_repos():
        cache.track_repo(repo)

    while True:
        while cache.empty() and not cache.user_empty():
            track_user(cache.pop_user())

        if cache.empty() and cache.user_empty():
            break

        repo = cache.pop_repo()
        if repo.is_cheating():
            cache.tag_cheat_user(repo.owner)
            cache.tag_cheat_repo(repo)
            print(repo.id, repo.owner.login, repo.name, repo.stargazers_count, '-> cheat',
                  repo.fake_count, '/', repo.real_count, repo.reason)
        else:
            print(repo.id, repo.owner.login, repo.name, repo.stargazers_count, '-> ok',
                  repo.fake_count, '/', repo.real_count, repo.reason)

    cache.markdown()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--track", dest="bait",
                        help="track cheat users from USER", metavar="USER")
    parser.add_argument("-r", "--repo", dest="repo",
                        help="track cheat users from REPO", metavar="REPO")
    args = parser.parse_args()

    if args.bait:
        track(args.bait)
    elif args.repo:
        print(args.repo)
    else:
        parser.print_help()
