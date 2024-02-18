"""
=====================================================================
Grammar for the first comment in a PR.

Template of a PR's first comment (a.k.a PR's body) should be found in the following file:
  <project_root>/.gitignore/pull_request_template.md


The following TOKENS will be used by the parser:
  "ticket_number"    # number of the ticket
  "ticket_url"       # url of the ticket
  "ticket_title"     # description of the ticket
  "type"             # type of the issue - bug, enhancement, etc.
  "topic"            # topic of the issue - domain name
  "is_highlight"     # yes/no - add the PR's description to highlight of the release notes
  "include"          # yes/no - include the PR in release notes
  "description"      # description of the PR
  "image_md"         # image url in mark down if any

To read more about `parsimonious` grammar templates:
  https://realpython.com/primer-on-jinja-templating/

=====================================================================
"""


def sequence_to_regex(sequence: list[str]) -> str:
    "Helper function that convert the given list to regex with the given valid values"
    res = '|'.join(sorted(sequence))
    return fr'~r"({res})"'


string_regex       = r'~r"[\w| |\n|_|\.|,|\'|\-|:]+"'
url_string_regex   = r'~r"[\w|/|:|#|=|\.|_]+"'
bool_regex         = r'~r"(yes|no)"i'
image_string_regex = r'~r"!\[image\]\(.*?\)"i'

# Define the issue types:
all_types = [
    "Bug",
    "Enhancement",
]
# Grammar:
fr"""
    # Top of tree:
    release_notes           = etc release_notes_name ticket_line type_line topic_line highlight_line ignore_line description_line image_line rest

    # Grammar rules:
    ticket_line             = etc ticket_name etc lspar lspar ticket_number rspar lpar ticket_url rpar rspar ws dash ws tick ticket_title tick etc ticket_line*
    type_line               = etc type_name etc tick type tick  etc
    topic_line              = etc topic_name etc tick topic tick  etc
    highlight_line          = etc highlight_name etc tick is_highlight tick
    ignore_line             = etc ignore_name etc tick include tick
    description_line        = etc description_name etc three_tick text_name ws description three_tick
    image_line              = etc image_md*

    # Tokens for release notes:
    ticket_number  = {string_regex}
    ticket_url     = {url_string_regex}
    ticket_title   = {string_regex}
    type           = {string_regex}
    topic          = {string_regex}
    is_highlight   = {bool_regex}
    include        = {bool_regex}
    description    = {string_regex}
    image_md       = {image_string_regex}

    # Const names:
    release_notes_name      = "Release notes:"
    ticket_name             = "Ticket"
    type_name               = "Tag"
    topic_name              = "Topic"
    highlight_name          = "Highlight"
    description_name        = "Description"
    ignore_name             = "Add to release notes"
    text_name               = "text"

    # Special characters:
    etc                     = ~r"[#|\*|:| |\s]*"  # mark down characters or new \s
    rest                    = ~r"(.|\s)*"
    ws                      = ~"\s*"
    lspar                   = "["
    rspar                   = "]"
    lpar                    = "("
    rpar                    = ")"
    tick                    = "`"
    three_tick              = "```"
    dash                    = "-"
"""
