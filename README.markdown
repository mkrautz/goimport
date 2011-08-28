What is GoImport?
=================

GoImport is a Sublime Text 2 plugin that helps you with handling import
statements in your Go programs.  It's inspired by the :Import/:Drop support
for VIM that's bundled with the Go language.

Installing it
=============

Simply clone this repo to your Packages directory.  On Mac OS X, this would be:

 $ cd ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/
 $ git clone git://github.com/mkrautz/goimport.git GoImport

After cloning the repo, you'll also need to add keybinds for activating the import
and drop prompts.  My user keybinds look like this:

 [
     { "keys": ["f1"], "command": "prompt_go_import" },
     { "keys": ["f2"], "command": "prompt_go_drop" }
 ]

Keybinds can be configured via the Preferences -> Key Bindings (User) menu.

Using it
========

After installation, you should be able to use your chosen keyboard shortcuts to handle
your imports.  For example, I simply press F1 when I want to add a new import, and F2 to
drop an existing one.  Note that as of this writing, when adding an import, the existing
imports will be sorted alphabetically.

TODO
====

Named importrs are not handled too well at the moment.
