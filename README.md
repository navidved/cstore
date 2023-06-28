![cstore_logo_mini](https://github.com/navidved/cstore/assets/31470742/e0f5ae54-3c52-4f06-aa8b-e2d67e296dc4)
# CStore
CStore or Command Store is an open text CLI software based on Python, which allows you to easily save commands that you may forget, and then search and retrieve them using keywords, descriptions, or tags.

CStore is designed as a secure place to store passwords and access tokens. While it's common to save such items in text files on the local system, this practice is not secure. With CStore, you can safely store, search, and retrieve these sensitive items. This feature is particularly useful for terminal enthusiasts and server administrators. The stored commands are securely encrypted and saved in a database, and can only be accessed with a password. Furthermore, the commands stored in CStore are not recorded in the terminal history, ensuring maximum security. 

## Key Features
* **Easy store & retrieve:** Easily save and retrieve commands you frequently use.
* **Secure store:** Securely store passwords and access tokens.
* **Powerful Search:** Search and retrieve commands using keywords, descriptions, or tags.

## Details
CStore also known as Command Store, is an open-source command-line interface (CLI) software built with Python. It provides an easy way to save commands that you might forget and enables you to search and retrieve them based on command text, descriptions, or tags.

CStore serves as a secure repository for storing passwords and access tokens. While it's common to store such sensitive information in local text files, it is not a secure practice. With the CStore feature, you can conveniently and safely store, search, and retrieve these items. This functionality is particularly valuable for terminal enthusiasts and server administrators. Commands are securely encrypted, stored in a database, and can only be accessed with a password. Importantly, commands stored in CStore are not recorded in the terminal history, ensuring enhanced security during both saving and recovery processes.

Each command can consist of up to 500 characters, and you can provide a description of up to 1000 characters. Additionally, you have the option to assign tags to each command. After a suitable recovery period, you can enter a portion of the command or its description into CStore and obtain a list of related commands to choose from. The selected command is then conveniently saved to the clipboard, ready for pasting wherever you need it.

By utilizing the tags you define, you can retrieve a list of commands associated with a specific tag or filter search results using tags. This allows for better organization and efficient retrieval of commands based on relevant categories.

### Installation
`$ pip install cstore`

### Usage
### Searching and Filtering Commands
> To search for a command or filter commands based on a specific keyword or description, **just type cstore and enter!** or use the following command:

`$ cstore -c "<part of target command or description>"`

> To search and **filter** commands based on **tags**, use the following command (you can use multiple tags):

`$ cstore -c "<part of target command or description>" -t <tag name>`

### Managing Tags
> To see the list of available **tags** and retrieve a list of commands related to a tag, use the following command:

`$ cstore tags`

### Adding New Commands
> To add a new command, use the following command:

`$ cstore -ac "<your command>"`

> You can add a description to the command using the --desc option:

`$ cstore -ac "<your command>" --desc "<your command description>"`

> You can also add tags to the command using the -t option (you can add multiple tags):

`$ cstore -ac "<your command>" -t <tag name>`

> for example

`$ cstore -ac "docker ps --all"  --desc "show both running and stopped containers" -t docker

### adding Secure Commands (passwords & tokens)
> To add a command in secure mode use the --secret option. **In secure mode, you cannot add a description. Instead, use the command itself to provide a name for your secure command.**:

`$ cstore -ac "<your command>" --secret`

### Deleting Commands
> To delete a commands, use the following command:

`$ cstore -dc "<part of command or description that you want to delete>"`

> To delete all commands associated with a specific tag, use the following command:

`$ cstore -dt <tag name>`

> To delete all saved commands, use the following command:

`$ cstore flush`

### Command Information
> To display information about a command, use the following command:

`$ cstore -sc "<part of command or description>"`

### Importing Commands
> You can define commands as a JSON file and import them using the import command. To import commands from a JSON file, use the following command:

`$ cstore import --path "<your json file path>"`

### Join Us Today!
  ### Upcoming Features and Improvements for "CStore"
* Export commands: Ability to export commands in general or by specific tags.
* Command and tag editing: Edit existing commands and tags within "CStore."
* Completing verbose: Improved verbose mode for better command execution understanding.
( Code structure and comments: Enhancing code structure and adding comprehensive comments.
* Join us in shaping the future of "CStore" by contributing to these exciting features and improvements. Stay tuned for updates!

> Special thanks to the developers of the following packages:
  - pydantic
  - typer
  - cryptocode
  - pyperclip
  - simple_term_menu
  - rich
  - SQLAlchemy
