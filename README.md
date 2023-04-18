<p align="center">
<img src="./docs/images/logo.png" width=250 height=100/>
</p>
<br>
<h2 align="center">Auto generate release notes from GitHub</h2>

# Usage
## Interactive
* **Run**:  
  [![Open All Collab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/dyeheske/rnotes/blob/master/docs/rnotes.ipynb)

## CLI
  1. **Clone** the repository:
      ```bash
      git clone https://github.com/dyeheske/rnotes.git
      ```
  2. **Install** dependencies:
      ```bash
      pip3 install -r docs/requirements.txt
      ```
  3. **Set** your personal [GitHub token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) to environment variable:<br>
      *csh* example of a dummy token:
      ```bash
      setenv GITHUB_TOKEN gdp_Vj34lfnjvA42oaocm4knt235ZA
      ```
  4. **Run**:
      ```bash
      python rnotes/rnotes.py generate \
          --repository_name="dyeheske/dummy_tool" \
          --from_tag="v0.1" \
          --to_tag="v0.2"
      ```

# Pre requests
Your GitHub repository should have the following files:
```text
📁 top directory
├── 📁 .rnotes
│   ├──📄 grammar.py
│   ├──📄 additional_content.py
│   └──📄 release_notes.j2
├── 📁 .github
│   ├──📄 pull_request_template.md
│   ├── ...
...
```
An **example** of such repository can be found here: [dyeheske/dummy_tool](https://github.com/dyeheske/dummy_tool)

### Note:<br>
It is not mandatory to have these files because it is possible to pass them as inputs files, by running *rnotes* via the CLI.

# Authors
See [AUTHORS.md](https://github.com/dyeheske/rnotes/blob/master/AUTHORS.md)
