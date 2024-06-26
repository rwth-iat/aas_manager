# Technical guidelines

Deviations from guidelines are permitted in individual cases, if necessary after discussion.

## Miscellaneous

- We prefer text formats like JSON.
- We use [Semantic Linefeeds](https://rhodesmill.org/brandon/2012/one-sentence-per-line/) in text files,
  aka "one sentence per line."


## Version control

- We use Git for version control.
- We use the [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow), which means one new branch per feature.
    - Code is merged into `master` only after successful review.
    - Code in `master` should be functional and rollable at all times.
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

## Coding

- Our standard programming language is Python 3.7.
- We write code (variable names, comments) and commit messages in English.
- We record external dependencies in a structured way, e.g. in `requirements.txt`.
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
    - We prefer "explicit relative imports" over "absolute imports" (the opposite of PEP).
      (After [Modules and Packages: Live and Let Die](https://www.youtube.com/watch?v=0oTh1CXRaQ0&t=18m52s))
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
