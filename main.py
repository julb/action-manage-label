#!/usr/bin/python3
import json
import os
import requests
import yaml
from github import Github


def _format_input_label(input_label):
    """ Formats the input label into a valid configuration. """
    return {
        'name': input_label['name'],
        'color': (input_label['color'][1:] if input_label['color'].startswith('#') else input_label['color']),
        'description': input_label['description'] if 'description' in input_label else ''
    }


def _read_input_from(input_from):
    """ Reads the labels from the input from. """
    inputs = []

    for input_from_line in input_from.splitlines():
        # Normalize file path.
        input_from_line = input_from_line.strip()

        # Skip if line is empty.
        if not input_from_line:
            continue

        # Load file content
        print(f"::debug::Loading labels from '{input_from_line}'.")
        input_from_content = None
        if input_from_line.startswith('http://') or input_from_line.startswith('https://'):
            requests_url_response = requests.get(input_from_line)
            if requests_url_response.ok:
                input_from_content = requests_url_response.text
            else:
                raise Exception(f'Unable to read file from {input_from_line}: {requests_url_response.reason}')
        else:
            with open(input_from_line, 'r', encoding="utf8") as input_from_file:
                input_from_content = input_from_file.read()

        if input_from_line.endswith('.yaml') or input_from_line.endswith('.yml'):
            inputs.extend(yaml.load(input_from_content, Loader=yaml.FullLoader))
        if input_from_line.endswith('.json'):
            inputs.extend(json.loads(input_from_content))

    return inputs


def main():
    """ The main method executed. """

    # Input variables
    github_token = os.environ.get('GITHUB_TOKEN')
    github_repository = os.environ.get('GITHUB_REPOSITORY')
    input_from = os.environ.get('INPUT_FROM', '.github/config/labels.yml')
    input_skip_delete = os.environ.get('INPUT_SKIP_DELETE', 'false').lower() == 'true'

    # Get repository.
    github = Github(github_token)
    github_repo = github.get_repo(github_repository)

    # Load provided labels.
    github_configured_labels = _read_input_from(input_from)
    github_configured_labels_dict = {}
    for github_label in github_configured_labels:
        github_configured_labels_dict[github_label['name']] = _format_input_label(github_label)

    # Create a dict of existing labels.
    github_existing_labels_dict = {}
    for github_label in github_repo.get_labels():
        github_existing_labels_dict[github_label.name] = github_label

    # Create.
    label_names_to_create = github_configured_labels_dict.keys() - github_existing_labels_dict.keys()
    for label_name_to_create in label_names_to_create:
        label_to_create = github_configured_labels_dict[label_name_to_create]
        print(f"::debug::Creating '{label_to_create['name']}' label with color '{label_to_create['color']}'.")
        github_repo.create_label(
            name=label_to_create['name'],
            color=label_to_create['color'],
            description=label_to_create['description']
        )

    # Update existing
    label_names_to_update = list(set(github_existing_labels_dict.keys()) & set(github_configured_labels_dict.keys()))
    for label_name_to_update in label_names_to_update:
        label_to_update = github_configured_labels_dict[label_name_to_update]
        github_existing_label = github_existing_labels_dict[label_name_to_update]

        if github_existing_label.color != label_to_update['color'] \
           or github_existing_label.description != label_to_update['description']:
            print(f"::debug::Updating '{label_to_update['name']}' label with color '{label_to_update['color']}'.")
            github_existing_label.edit(
                name=label_to_update['name'],
                color=label_to_update['color'],
                description=label_to_update['description']
            )
        else:
            print(f"::debug::Nothing to do for '{label_to_update['name']}' : same color and description.")

    # Delete unexisting.
    if not input_skip_delete:
        label_names_to_delete = github_existing_labels_dict.keys() - github_configured_labels_dict.keys()
        for label_name_to_delete in label_names_to_delete:
            print(f"::debug::Deleting the label '{label_name_to_delete}'.")
            github_existing_labels_dict[label_name_to_delete].delete()
    else:
        print('::debug::Do not delete existing labels.')


if __name__ == "__main__":
    main()
