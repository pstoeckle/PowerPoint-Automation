# PowerPoint Automation

I wrote these scripts during my time at the [Technical University of Munich (TUM)](https://www.tum.de/en/).
The goal of these scripts is to ease tasks in the context of PowerPoint, especially in the context of lectures.

## Usage

```shell
$ powerpoint-automation --help
Usage: powerpoint-automation [OPTIONS] COMMAND [ARGS]...

  Scripts to automate some task in the context of PowerPoint.

Options:
  --version                       Version
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.

Commands:
  add-git-metadata-as-footer      Adds a footer to the...
  add-git-metadata-as-presentation-metadata
                                  This commands adds git...
  convert-presentations           Converts PowerPoint files to...
  git-pptx-diff                   :return:
  remove-picture                  Remove the pictures from all...
  replace-date                    Replace a date in the...
```

### Replace Date

```shell
$ powerpoint-automation replace-date --help
Usage: powerpoint-automation replace-date [OPTIONS] [INPUT_DIRECTORY_PATH]

  Replace a date in the slides, e.g., 2020 -> 2021. This is especially handy
  at the beginning of a new semester where you have to update the slides of
  the previous year.

Arguments:
  [INPUT_DIRECTORY_PATH]  [default: .]

Options:
  -O, --old-year INTEGER  [default: 2020]
  -N, --new-year INTEGER  [default: 2021]
  --help                  Show this message and exit.
```

### Add git Metadata as Footer

```shell
$ powerpoint-automation add-git-metadata-as-footer --help
Usage: powerpoint-automation add-git-metadata-as-footer [OPTIONS]
                                                        [INPUT_DIRECTORY_PATH]

  Adds a footer to the PowerPoint slides with the latest commit's hash and
  date.

Arguments:
  [INPUT_DIRECTORY_PATH]  [default: .]

Options:
  --help  Show this message and exit.
```

### Add git Metadata as

```shell
$ powerpoint-automation add-git-metadata-as-presentation-metadata --help
Usage: powerpoint-automation add-git-metadata-as-presentation-metadata
           [OPTIONS] [INPUT_DIRECTORY_PATH]

  This commands adds git metadata to the PowerPoint slides, e.g., the commit,
  the authors, etc.

Arguments:
  [INPUT_DIRECTORY_PATH]  [default: .]

Options:
  -a, --author TEXT
  --help             Show this message and exit.
```

### Convert Presentations

```shell
$ powerpoint-automation convert-presentations --help
Usage: powerpoint-automation convert-presentations [OPTIONS]
                                                   [INPUT_DIRECTORY_PATH]

  Converts PowerPoint files to PDFs. This is especially handy if you want to
  create many PDFs without exporting them manually one by one.

Arguments:
  [INPUT_DIRECTORY_PATH]  [default: .]

Options:
  -o, --output-directory DIRECTORY
                                  [default: dist]
  -L, --libre-office FILE         [default: /Applications/LibreOffice.app/Cont
                                  ents/MacOS/soffice]
  -s, --skip-file TEXT
  --help                          Show this message and exit.
```

## Contact

If you have any question, just write [me](mailto:patrick.stoeckle@posteo.de) an email.
