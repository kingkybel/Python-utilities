import argparse
import os
from jira import JIRA

class JiraAutomation:
    def __init__(self, server: str, username: str, token: str):
        """
        Initialize the JiraAutomation object.

        :param server: URL of the Jira server
        :param username: Username for Jira login
        :param token: API token for authentication
        """
        options = {'server': server}
        self.__jira = JIRA(options=options, basic_auth=(username, token))
        self.__boards = {}
        self.__projects = {}

    def list_boards(self):
        """
        Lists all boards available to the user.
        """

        def sorter(b):
            try:
                b.location.projectKey
            except AttributeError:
                return ""
            return b.location.projectKey

        boards = self.__jira.boards()
        boards.sort(key=sorter)
        counter = 0
        for board in boards:
            try:
                project_key = board.location.projectKey
            except AttributeError:
                project_key = f"GENKEY{counter}"
                counter += 1
            self.__boards[project_key] = (board.id, board.name)
            print(f"{project_key}:\tName: {board.name}, Board ID: {board.id}")

    def list_user_ticket_statuses(self, user: str):
        """
        Lists the statuses of tickets assigned to a specific user.

        :param user: Jira username
        """
        jql_query = f"assignee = '{user}'"
        issues = self.__jira.search_issues(jql_query)
        print(f"Tickets assigned to '{user}':")
        for issue in issues:
            print(f"{issue.key}: {issue.fields.summary} - Status: {issue.fields.status.name}")

    def list_projects(self):
        """
        Lists all accessible Jira projects and their keys.
        """

        def sorter(proj):
            return proj.key

        projects = self.__jira.projects()
        projects.sort(key=sorter)
        print("Accessible Jira Projects:")
        for project in projects:
            self.__projects[project.key] = (project.id, project.name)
            print(f"Key: {project.key}\tid: {project.id}\tName: {project.name}")

    def create_ticket(self, project_key: str, summary: str, description: str, issue_type: str = "Task"):
        """
        Creates a new Jira ticket.

        :param project_key: Project ID where the ticket should be created
        :param summary: Summary of the ticket
        :param description: Detailed description of the ticket
        :param issue_type: Type of the issue (e.g., Task, Bug, Story)
        :return: The created issue
        """
        project_id = self.__projects[project_key][0]
        issue_dict = {
            'project': {'id': project_id},
            'summary': f"{summary}",
            'description': f"{description}",
            'issuetype': {'name': f"{issue_type}"},
        }

        new_issue = self.__jira.create_issue(fields=issue_dict)
        print(f"Issue {new_issue.key} created successfully.")
        return new_issue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate Jira tasks.")
    parser.add_argument("--server", "-s",
                        type=str,
                        default=None,
                        help="jira server url")
    parser.add_argument("--username", "-u",
                        type=str,
                        default=None,
                        help="user-name for jira login")
    parser.add_argument("--password", "-p",
                        type=str,
                        default=None,
                        help="password for jira login. If not set then environment variable " \
                             "'JIRA_PASSWORD' is used.")
    parser.add_argument("--jira-api-token", "-j",
                        type=str,
                        default=None,
                        help="Access token to the Jira API. If not set then environment variable " \
                             "'JIRA_API_TOKEN' is used.")
    parser.add_argument("--jira-project-key", "-k",
                        type=str,
                        default=None,
                        help="Jira project-key.")
    parser.add_argument("--full-name-for-ticket-statuses", "-f",
                        type=str,
                        default=None,
                        help="Username to check ticket statuses for.")
    args = parser.parse_args()

    jira_server = os.getenv("JIRA_SERVER", args.server)
    username = os.getenv("JIRA_USERNAME", args.username)
    api_token = os.getenv("JIRA_API_TOKEN", args.jira_api_token)

    # Create an instance of JiraAutomation
    jira_automation = JiraAutomation(jira_server, username, api_token)

    # List all boards
    print("Available Boards:")
    jira_automation.list_boards()

    # List statuses of tickets assigned to a specific user
    if args.full_name_for_ticket_statuses is not None:
        print(f"\nUser Ticket Statuses for user {args.full_name_for_ticket_statuses}:")
        jira_automation.list_user_ticket_statuses(args.full_name_for_ticket_statuses)

    jira_automation.list_projects()

    # Create a new ticket
    if args.jira_project_key is not None:
        print("\nCreating a Ticket:")
        jira_automation.create_ticket(
            project_key=args.jira_project_key,
            summary="Sample Ticket Summary created from automation",
            description="Detailed description of the sample ticket.",
            issue_type="Task"
        )
