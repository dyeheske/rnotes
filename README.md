<p align="center">
<img src="./docs/images/logo.png" width=250 height=100/>
</p>
<h2 align="center">Auto generate release notes from GitHub</h2>

Rnotes generates release notes file for any GitHub repository by gathering, parsing and processing all the changes that done between 2 tags. To generate release notes, there are 2 ways: interactive mode, using Jupyter Notebook, or CLI mode. Note that you need to make sure you have all the pre requests before running this tool.
# Contents
- [Contents](#contents)
- [Usage](#usage)
  - [Interactive](#interactive)
  - [CLI](#cli)
- [Pre requests](#pre-requests)
- [How it works?](#how-it-works)
- [Authors](#authors)

# Usage

## Interactive
* **Run** in Jupyter Notebook:  
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
  1. Your GitHub repository should have the following files:
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
      An **example** of such repository can be found here: [dyeheske/dummy_tool](https://github.com/dyeheske/dummy_tool)<br><br>
      (note that it is not mandatory to have these files because it is possible to pass them as inputs files, by running *rnotes* via the CLI or Python API)<br>

  2. In order to generate release notes, you **must** have a personal access token (a.k.a PAT), and if you don't have yet you can see how to do it [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token#creating-a-personal-access-token-classic). This will allow the tool to query GitHub data base and also allow you to generate release notes for a private GitHub repositories and protected repositories (like enterprise's repositories).


# How it works?
The algorithm to generate release notes is the following:<br>
  1. Fetch all the pull requests between the period of time of the given 2 tags (the commit date that every tag is attached to) from the given GitHub repository and get their first comment text ([tree example ↗️](https://github.com/dyeheske/rnotes/blob/master/docs/images/tags_in_dummy_tool.png)).
  2. Parse every comment text based on the given grammar file.
  3. Process all the data and order it.
  4. Write the data based on the given template file.

See the following diagrams of the rnotes flow with the needed inputs/output:  
  * [General diagram ↗️](https://github.com/dyeheske/rnotes/blob/master/docs/images/rnotes_black_box.png)
  * [Detailed diagram ↗️](https://github.com/dyeheske/rnotes/blob/master/docs/images/rnotes.png)


# Authors
See [AUTHORS.md](https://github.com/dyeheske/rnotes/blob/master/AUTHORS.md)
