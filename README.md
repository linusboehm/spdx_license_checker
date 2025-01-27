# SPDX license checker

Checks all files for an SPDX license identifier. Checks each added file for lines that match
`<comment_sting>\s*SPDX-License-Identifier:.*` and adds the defined license identifier, if it is
missing.

Pre-commit configuration:

```yaml
- repo: https://github.com/linusboehm/spdx_license_checker
  hooks:
    - id: spdx-license-checker
      args:
        - "--license=Apache-2.0 WITH LLVM-exception" # add desired license identifier here
```
