# Technical guidelines

Deviations from guidelines are permitted in individual cases, if necessary after discussion.

## Miscellaneous

- We prefer text formats like JSON.
- We use [Semantic Linefeeds](https://rhodesmill.org/brandon/2012/one-sentence-per-line/) in text files,
  aka "one sentence per line."


## Version control

- We use Git for version control.
- We use the [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), which means one new branch per feature.
    - Feature and fix branches start from `master`, and their pull requests target `master`.
    - Code is merged into `master` only after successful review.
    - Code in `master` should be functional and rollable at all times.
- We release by tag, not by merge:
    1. Bump `version` in `pyproject.toml` on `master`.
    2. Push a tag `vX.Y.Z` with the same version, e.g. `git tag v0.5.1 && git push origin v0.5.1`.
    3. The release workflow builds the packages and creates the GitHub release.
    - A fix for an older release goes on a branch `release/X.Y.x` created from its tag, only when needed.
- Commits reference their GitHub issue in the body, e.g. `Fixes #87` or `Refs #87`.
- We follow [The seven rules of a great Git commit message](https://chris.beams.io/posts/git-commit/#seven-rules), but use bodies only when necessary:
  ```
    1. Separate subject from body with a blank line
    2. Limit the subject line to 50 characters
    3. Capitalize the subject line
    4. Do not end the subject line with a period
    5. Use the imperative mood in the subject line
    6. Wrap the body at 72 characters
    7. Use the body to explain what and why vs. how
  ```

## Testing

- We write a failing test first, then the fix (test-driven development).
- Tests live in `aas_editor_test/` and run headless:
  ```sh
  QT_QPA_PLATFORM=offscreen uv run --extra dev python -m pytest aas_editor_test --ignore=aas_editor_test/main_test.py
  ```
- `main_test.py` is a full GUI integration test and is excluded from CI.

## Coding

- Our standard programming language is Python 3.11 or newer (required by the basyx fork).
- We write code (variable names, comments) and commit messages in English.
- We record external dependencies in `pyproject.toml`; `uv.lock` pins the resolved versions.
- The static part of error messages and log messages comes before the dynamic part if possible.  
  Good:
  ```py
  #                         static        dynamic
  #                           ↓               ↓
  raise ValueError(f"Malformed response: '{response}'")
  ```
  Bad:
  ```py
  #                     static       dynamic      static
  #                       ↓             ↓            ↓
  raise ValueError(f"The response '{response}' was malformed.")
  ```
  This makes it easier to read and filter longer output because the constant parts always stay together and in the same place.

## Python

- We use the [PEP 8 Coding Style](https://www.python.org/dev/peps/pep-0008/) with the following adjustments:
    - Lines can be up to 88 characters long
    - Strings exclusively with double quotation marks (")
    - We use absolute imports throughout (`from aas_editor.subpackage.module import Symbol`).
    - We follow naming conventions of Qt and use mixedCase naming style for variables and CamelCase for class names.
  
        Allowed:
        ```py
        GLOBAL_VARIABLE = 1
        variable = 1
        exampleVariable = 1
  
        class ExampleClass:
            pass
        class Example:
            pass
        ```
        Not allowed:
        ```py
        variable_a = 1
        variable_a = 10
  
        class Example_class:
            pass
        class Example_Class:
            pass
        ```  

- We use [f-strings](https://www.python.org/dev/peps/pep-0498/) for concatenation of strings.    
  Allowed:
  ```py
  f"{baseURL}/{objectName}/{method}/{taskId}"
  ```
  Not allowed:
  ```py
  base_url + "/" + object_name + "/" + method + "/" + task_id
  "%s/%s/%s/%d" % (baseURL, objectName, method, taskId)
  "{}/{}/{}/{}".format(baseURL, objectName, method, taskId)
  ```
- We prefer [pathlib](https://docs.python.org/3/library/pathlib.html) instead
  [os.path](https://docs.python.org/3/library/os.path.html) and
  [open()](https://docs.python.org/3/library/functions.html#open).
- Executable scripts start with the following shebang:
  ```
  #!/usr/bin/env python3
  ```
- Executable scripts call a dedicated `main()` function as follows
  ```py
  if __name__ == "__main__":
      main()
  ```
  This simplifies installation via 'setuptools', makes any tests easier and makes Lintern's analysis easier.
