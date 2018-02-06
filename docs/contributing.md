# Contributing to the project

Contributing to the opsdroid ecosystem is strongly encouraged and every little bit counts!

Things you can help with:
 - [Documentation](#documentation)
 - [Creating new modules](#new-modules)
 - [Issues](#issues)
     - [Squashing bugs](#quick-links)
     - [Enhance opsdroid](#quick-links)
 
If you need help or if you are unsure about something join our [gitter channel](https://gitter.im/opsdroid/)  and ask away! We are more than happy to help you.


## Workflow

All contributors to the project, including the project founder [jacobtomlinson](https://github.com/jacobtomlinson), contribute using the following process:

 * Fork the main project to your own account
 * Work on your changes on a feature branch
 * Create a pull request back to the main project
 * Tests and test coverage will be checked automatically
 * A project maintainer will review and merge the pull request

## Developing

```shell
# clone the repo
git clone https://github.com/opsdroid/opsdroid.git
cd opsdroid

# install the project in "editable" mode
pip install -e .

# run opsdroid
python -m opsdroid
```

Running the tests

```shell
# install test runner
pip install -U tox

# run tests
tox
```


## Developing in containers

Developing in containers can be a great way to ensure that opsdroid will run in a clean python environment and that all dependencies are captured.

```shell
# build the container
docker build -t opsdroid/opsdroid:myfeature .

# run opsdroid
docker run --rm -ti -v $(pwd):/usr/src/app opsdroid/opsdroid:myfeature
```

Running the tests

```shell
# run tests
docker run --rm -ti -v $(pwd):/usr/src/app opsdroid/opsdroid:myfeature tox
```

## Maintainer scripts

This project contains a directory called [`scripts`](https://github.com/opsdroid/opsdroid/tree/master/scripts) which are simple python scripts for use by maintainers when working on opsdroid. Each directory contains the script itself, a README and other supporting files. See the individual README files for more information.

_These scripts may have dependancies so you should run `pip install -r requirements_dev.txt` from the root of the project._

## Documentation
More documentation is always appreciated and it's something that you can contribute to from the GitHub web interface.  This might be a great start point if you are new to Open Source and GitHub!

Things that we need help with:
 
 - More documentation. Something that you think is unclear?
 - More examples on how to use opsdroid
 - More Tutorials
 - Typos/Grammar check
 - Blog posts, articles, etc
 - Any issue marked with the [documentation tag](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:documentation)

## Creating New Modules
Opsdroid is an open source chatbot framework. It is designed to be extendable, scalable and simple. It comes with a few official modules that can be found in the [Opsdroid  GitHub account](https://github.com/opsdroid).
 
 If you love a particular platform and wish to use opsdroid with it or if you want opsdroid to interact with something in a certain way you can create your own modules and extend the functionality of opsdroid.
 
 If you don't know where to start, make sure to check the [tutorials](tutorials) and read the [documentation](http://opsdroid.readthedocs.io/en/latest/?badge=latest).  Remember that you can also ask for help in our [gitter channel](https://gitter.im/opsdroid/)


## Issues
You can help us by reporting new issues or by fixing existing issues. 

If you find any part of opsdroid that's acting odd it would be great if you take the time to create a new issue. That will help us keep opsdroid free of any bugs.

We try to tackle issues as fast as possible, but help would be greatly appreciated. To get started, simply follow the [workflow guidelines](#workflow) and developing instructions.

##### Quick Links:
 - Skill level
    - [First timer](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:%22good+first+issue%22)
    - [Beginner](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:beginner)
    - [Intermediate](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:intermediate)
    - [Advanced](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:advanced)
 - [Squash Bugs](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:bug)
 - [Documentation](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:documentation)
 - [Enhancements](https://github.com/opsdroid/opsdroid/issues?q=is:issue+is:open+label:enhancement)
 
 Don't forget, you can always help with the modules found in [opsdroid repository](https://github.com/opsdroid).
 
 
## Credits

### Contributors

Thank you to all the people who have already contributed to opsdroid!
<a href="graphs/contributors"><img src="https://opencollective.com/opsdroid/contributors.svg?width=890" /></a>


### Backers

Thank you to all our backers! [[Become a backer](https://opencollective.com/opsdroid#backer)]

<a href="https://opencollective.com/opsdroid#backers" target="_blank"><img src="https://opencollective.com/opsdroid/backers.svg?width=890"></a>


### Sponsors

Thank you to all our sponsors! (please ask your company to also support this open source project by [becoming a sponsor](https://opencollective.com/opsdroid#sponsor))

<a href="https://opencollective.com/opsdroid/sponsor/0/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/0/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/1/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/1/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/2/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/2/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/3/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/3/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/4/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/4/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/5/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/5/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/6/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/6/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/7/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/7/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/8/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/8/avatar.svg"></a>
<a href="https://opencollective.com/opsdroid/sponsor/9/website" target="_blank"><img src="https://opencollective.com/opsdroid/sponsor/9/avatar.svg"></a>

<!-- This `CONTRIBUTING.md` is based on @nayafia's template https://github.com/nayafia/contributing-template -->