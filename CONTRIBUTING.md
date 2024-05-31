# Contributing to Scalpel

Thank you for your interest in contributing to Scalpel! This document outlines the process and guidelines for contributing to the project. By following these guidelines, you can help ensure a smooth collaboration process and a consistent codebase.

## Table of Content

-   [Setting Up Your Development Environment](#setting-up-your-development-environment)
-   [Building the Project](#building-the-project)
    -   [Building Scalpel](#building-scalpel)
    -   [Building the documentation](#building-the-documentation)
-   [Testing](#testing)
-   [Commit and Branch Format](#commit-and-branch-format)
    -   [Commit Messages](#commit-messages)
    -   [Branch Naming](#branch-naming)
-   [Submitting Changes](#submitting-changes)
-   [Feedback and Reviews](#feedback-and-reviews)
-   [Conclusion](#conclusion)

## Setting Up Your Development Environment

1. **Fork the Repository**: Start by forking the Scalpel repository to your own GitHub account.

2. **Clone Your Fork**: Once done, clone your repository to your local machine:

    ```sh
    git clone https://github.com/YOUR_USERNAME/scalpel.git
    ```

3. **Set Up the Upstream Remote**: Add the original Scalpel repository as an "upstream" remote:
    ```sh
    git remote add upstream https://github.com/ORIGINAL_OWNER/scalpel.git
    ```

## Building the Project

### Building Scalpel

1. Navigate to the project root directory.
2. Build the project:
    ```sh
    ./gradlew build
    ```
3. Upon successful build, the generated JAR file can be found in `./scalpel/build/libs/scalpel-*.jar`.

### Building the documentation

1. Navigate to the docs directory:
    ```sh
    cd docs/
    ```
2. Create a virtual environment and install the requirements from `requirements.txt`:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
3. Launch the build:
    ```sh
    ./build.py
    ```
4. The documentation HTML pages will be generated in `public/`

## Testing

Before submitting any changes, ensure that all tests pass. Run them as follows:

```sh
./run_tests.sh
```

## Commit and Branch Format

### Commit Messages

Commit messages should be clear and descriptive. They should follow the format:

```
<type>(<scope>): <short description>
```

-   **type**: Describes the nature of the change (e.g., `fix`, `feature`, `docs`, `refactor`).
-   **scope**: The part of the codebase the change affects (e.g., `editor`, `venv`, `framework`).
-   **short description**: A brief description of the change.

Example:

```
fix(editor): Resolve null reference issue
```

### Branch Naming

Branch names should be descriptive and follow the format:

```
<type>/<short-description>
```

-   **type**: Describes the nature of the branch (e.g., `feature`, `fix`, `docs`, `refactor`).
-   **short description**: A brief description of the branch's purpose, using kebab-case.

Example:

```
feature/hex-editor
```

## Submitting Changes

1. **Create a New Branch**: Based on the `main` branch, create a new branch following the branch naming convention mentioned above.

2. **Make Your Changes**: Implement your changes, ensuring code quality and consistency.

3. **Commit Your Changes**: Commit your changes following the commit message format.

4. **Pull from Upstream**: Before pushing your changes, pull the latest changes from the `upstream` main branch:

    ```sh
    git pull upstream main
    ```

5. **Push to Your Fork**: Push your branch to your forked repository.

6. **Open a Pull Request**: Go to the original Scalpel repository and open a pull request from your branch. Ensure that your PR is descriptive, mentioning the changes made and their purpose.

## Feedback and Reviews

Once your pull request is submitted, maintainers or contributors might provide feedback. Address any comments, make necessary changes, and push those updates to your branch.

## Conclusion

Your contributions are valuable in making Scalpel a robust and efficient tool. By adhering to these guidelines, you ensure a smooth and efficient collaboration process. Thank you for your contribution!
