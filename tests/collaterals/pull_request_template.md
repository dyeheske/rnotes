#
## Release notes:
* **Ticket**: [[12345](https://hsdes.intel.com/appstore/article/#/12345)] - `Title of the ticket as appears in HSD`
* **Tag**: `Bug`
* **Topic**: `Clock automation`
* **Highlight**: `No`
* **Add to release notes**: `Yes`
* **Description**:
  ```text
  A description about the PR, that will (eventually) be  written to the
  release notes of the tool, if "Add to release notes" set to True.
  ```
#
## Changes:
* Change 1: ...
  * Sub change 1: ...
* Change 2: ...
  * Sub change 1: ...

## Notes:
* Note 1: ...
* Note 2: ...

## Checklist:
- [X] **Unit tests** added for my changes.
- [ ] **Coverage** is 100% (for all the new code I added).
- [ ] **Code style** - I ran [black](https://github.com/psf/black)[^1] with the argument `-l 132` for the source files I changed/added, in a separate commit OR ran flake8 with has 0 errors.
- [ ] **Profiler** - I ran runtime profiling[^2] on at least 1 new unit test I added.

[^1]: Black is the Python code formatter that follow the [PEP8](https://pep8.org/) standard.
[^2]: More about runtime profiler can be found [here](https://pypi.org/project/pytest-profiling/).
