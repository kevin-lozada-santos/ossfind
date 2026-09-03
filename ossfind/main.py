import sys

from auth import github_login
from github_api import (
    search_repositories,
    search_good_first_issues,
    get_repository_language,
    get_user,
    get_authenticated_user,
    get_trending_repositories,
    GitHubAPIError
)
from token_storage import load_token
 
def show_banner():
    print("=" * 40)
    print("OSSFind - Open Source Finder")
    print("=" * 40)


def main():

    show_banner()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  ossfind login")
        print("  ossfind search <keyword> [--language <lang>]")
        print("  ossfind issues [--language <lang>] [--repository <owner/name>]")
        print("  ossfind user <username>")
        print("  ossfind whoami")
        print("  ossfind trending")
        return


    command = sys.argv[1]


    if command == "login":

        token = github_login()

        if token:
            print("Login completed successfully")
        else:
            print("Login failed")


    elif command == "search":

        if len(sys.argv) < 3:
            print("Please provide keyword")
            return

        keyword = sys.argv[2]
        language = None

        if "--language" in sys.argv[3:]:
            language_index = sys.argv.index("--language")
            if language_index + 1 >= len(sys.argv):
                print("Please provide a language after --language")
                return
            language = sys.argv[language_index + 1]

        try:
            repos = search_repositories(keyword, language=language)
        except GitHubAPIError as error:
            print(f"Search failed: {error}")
            return

        for index, repo in enumerate(repos, start=1):

            print(f"{index}. {repo['full_name']}")
            print("⭐ Stars:", repo["stargazers_count"])
            print("Language:", repo["language"])
            print("Description:", repo["description"])
            print("URL:", repo["html_url"])
            print("-" * 50)


    elif command == "issues":

        language = None
        repository = None

        if "--language" in sys.argv[2:]:
            language_index = sys.argv.index("--language")
            if (language_index + 1 >= len(sys.argv)
                    or sys.argv[language_index + 1].startswith("--")):
                print("Please provide a language after --language")
                return
            language = sys.argv[language_index + 1]

        if "--repository" in sys.argv[2:]:
            repository_index = sys.argv.index("--repository")
            if (repository_index + 1 >= len(sys.argv)
                    or sys.argv[repository_index + 1].startswith("--")):
                print("Please provide a repository after --repository")
                return
            repository = sys.argv[repository_index + 1]

        try:
            issues = search_good_first_issues(
                language=language,
                repository=repository
            )
        except GitHubAPIError as error:
            print(f"Issue search failed: {error}")
            return

        if not issues:
            print("No matching issues found.")
            return

        for index, issue in enumerate(issues, start=1):
            repository_name = issue["repository_url"].rsplit("/repos/", 1)[-1]
            labels = ", ".join(label["name"] for label in issue["labels"])

            try:
                repository_language = get_repository_language(issue["repository_url"])
            except GitHubAPIError as error:
                print(f"Could not fetch repository: {error}")
                return

            print(f"{index}. Repository:", repository_name)
            print("Issue:", issue["title"])
            print("Labels:", labels)
            print("URL:", issue["html_url"])
            print("Created:", issue["created_at"])
            print("Language:", repository_language or "Unknown")
            print("-" * 50)


    elif command == "user":

        if len(sys.argv) < 3:
            print("Provide username")
            return

        username = sys.argv[2]

        try:
            user = get_user(username)
        except GitHubAPIError as error:
            print(f"Could not look up user: {error}")
            return

        if user:
            print("Name:", user["name"])
            print("Followers:", user["followers"])
        else:
            print("User not found")


    elif command == "whoami":

        token = load_token()

        if not token:
            print("Please login first")
            return

        try:
            user = get_authenticated_user(token)
        except GitHubAPIError as error:
            print(f"Could not fetch account: {error}")
            return

        if user:
            print("Name:", user["name"])
            print("Username:", user["login"])
            print("Followers:", user["followers"])
            print("Profile:", user["html_url"])
        else:
            print("Unable to fetch user")


    elif command == "trending":

        try:
            repos = get_trending_repositories()
        except GitHubAPIError as error:
            print(f"Could not fetch trending repositories: {error}")
            return

        print("\n🔥 Trending Open Source Projects\n")

        for index, repo in enumerate(repos, start=1):

            print(f"{index}. {repo['full_name']}")
            print("⭐ Stars:", repo["stargazers_count"])
            print("Language:", repo["language"])
            print("URL:", repo["html_url"])
            print("-" * 50)

    else:

        print("Unknown command:", command)



if __name__ == "__main__":
    main()
