# Making a release

Occasionally the maintainers of the opsdroid project make a release, and
distribute it.  This document is the procedure they follow to do that.

## Background

When releasing, there are a couple of release artifacts which are built and distributed.

Currently opsdroid builds:

- A Python distribution on [pypi](https://pypi.org/project/opsdroid/)
- A Python distribution on [Conda Forge](https://github.com/conda-forge/opsdroid-feedstock)
- A container image on [Docker Hub](https://hub.docker.com/r/opsdroid/opsdroid/)

The building and distributing is automated by Travis CI and run when a [release is created](https://help.github.com/articles/creating-releases/) on GitHub.

## Creating a release

### Testing

Before creating the release do some final local testing:

- Checkout master and run the `tox` suite locally.
- Run opsdroid and do some manual testing to ensure there are no glaring issues.

### Increment the version number

As opsdroid follows [SemVer 2.0](http://semver.org/) (`major.minor.patch`) the version number increase will depend on what has changed since the previous release.

- If the release includes only bug fixes then only the `patch` will be incremented. (See [Backports](#Backports) section for making patches)
- If the release includes new features then the `minor` will be incremented and the `patch` will be reverted to `0`.
- If the release includes changes which break backward compatibility then the `major` will be incremented with the `minor` and `patch` being reverted to `0`. However this only applies once opsdroid is above `v1.0.0`.

Keep a note of what the new version will be as it will be needed later.

### Generate release text

The release description to be posted on GitHub should be a bulleted list of changes separated into sections for **Enhancements**, **Bug fixes**, **Breaking changes** and **Documentation updates**. Each bullet should be the PR name and number which introduced the change.

It is possible to partially automatically generate this using a utility script:

```shell
# Pull the tags from opsdroid/opsdroid so that only commits since the last tag are listed
git pull upstream master --tags
# List the commits
python scripts/release_notes/release_notes.py
```

This will print a list of all the commits in the history since the last release, which due to the "squash and merge" feature in GitHub will be correctly formatted into one commit per PR with the title and number.

_You will need to add markdown bullets, sort into sections, tidy up the names and remove anything which is not relevant to the application itself (e.g changes to the GitHub PR and Issue templates). This can be done when drafting the release._

### Backports

As opsdroid releases are infrequent they often include many differen't PRs, which usually results in a `minor` release as at least one PR will introduce a new feature.

In the mean time there may be bug fixes merged into master which we want to release on a shorter timescale, these should be backported into the current minor version.

Steps

```console
# Pull down all tags
$ git pull upstream master --tags

# Checkout the latest tag
$ git checkout x.x.x

# Create a new dev branch for this minor version (e.g dev-0.14.x for the 0.14 minor release)
$ git checkout -b dev-x.x.x

# Cherry pick the bug fix from master
$ git cherry-pick -x <COMMIT HASH>

# Push branch to your fork and open a PR to the upstream branch
$ git push origin dev-x.x.x
```

Once tests have passed and you merge the patch into the dev branch you can perform a new release which targets the dev branch following the rest of this guide.

### Draft the release

Following steps 1-3 of the [GitHub releases guide](https://help.github.com/articles/creating-releases/) draft a new release.

Set the "Tag version" and "Release title" to the version number prefixed with the letter `v` (e.g `v0.9.1`). Ensure the tag target points to `master`.

Copy and paste the release text into the description section and make the changes specified above.

### Publish the release

Once you are happy with the release notes click "Publish release".

This will result in a number of automated actions:

- The new [release tag](https://github.com/opsdroid/opsdroid/tags) will be created on GitHub.
- [Travis CI](https://travis-ci.org/opsdroid/opsdroid) will build the [pypi distribution](https://pypi.python.org/pypi/opsdroid) and upload it.
- [Docker Hub](https://hub.docker.com/r/opsdroid/opsdroid/) will build a new container image, create the [new release tag](https://hub.docker.com/r/opsdroid/opsdroid/tags/) and also update `latest` to point to this release.
- The @opsdroid [twitter account](https://twitter.com/opsdroid) will tweet that the release has been generated (via [IFTTT](https://ifttt.com)).

There are also the following manual actions which need to be performed:

- A PR will automatically be raised on the [opsdroid feedstock on Conda Forge](https://github.com/conda-forge/opsdroid-feedstock). This needs to be reviewed and merged.

### Announce the release

If the version is not a simple `patch` release then the last action is to write a post on the @opsdroid [Medium blog](https://medium.com/opsdroid) about the release.

_If it is a `patch` release then add a note to the bottom of the last release blog post._

This post should include some preamble about the contents of the release, highlighting anything particularly exciting. It should then include a copy of the release notes.
