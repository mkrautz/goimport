# Copyright (c) 2011 Mikkel Krautz
# The use of this source code is goverened by a BSD-style
# license that can be found in the LICENSE-file.

from __future__ import unicode_literals
import sublime, sublime_plugin
import golex

class ImportMutator(object):
	'''
		An import mutator is an object that mutates
		the contents of a view to add or remove
		imports from a Go source file.

		A mutator is single-use only. It must be discarded
		after it has done one operation.
	'''

	def __init__(self, view):
		self.view = view
		src = self.view.substr(sublime.Region(0, view.size()))
		lexer = golex.Lexer(src)
		lexer.lex()
		self.tokens = lexer.tokens

		self.importStmtIdx = -1
		self.importEndIdx = -1
		self.findImportStmt()
	
	def findImportStmt(self):
		for idx, tok in enumerate(self.tokens):
			if tok.kind == golex.IDENTIFIER and tok.value == 'import':
				self.importStmtIdx = idx
				break

	def importedPkgs(self):
		pkgs = []
		tokens = self.tokens[self.importStmtIdx+1:]
		if len(tokens) == 0:
			return pkgs

		# Multiple imports	
		err = False
		name = None
		if tokens[0].kind == golex.LPAREN:
			for idx, tok in enumerate(tokens[1:]):
				# Break on end
				if tok.kind == golex.RPAREN:
					self.importEndIdx = self.importStmtIdx+1+1+idx
					break
				if name is not None:
					if tok.kind != golex.STRINGLIT:
						err = True
						break
				# Named import
				if tok.kind == golex.IDENTIFIER:
					name = tok
					continue
				# Unnamed import or package-part of named import
				if tok.kind == golex.STRINGLIT:
					# Named import
					if name:
						pkgs.append((name.value, tok.value[1:-1]))
						# Drop the name for the next import
						name = None
					else:
						pkgs.append((None, tok.value[1:-1]))
		# Single import
		else:
			# Named import
			if tokens[0].kind == golex.IDENTIFIER and len(tokens) > 1:
				pkgs.append((tokens[0].value, tokens[1].value[1:-1]))
			# Unnamed package
			elif tokens[0].kind == golex.STRINGLIT:
				pkgs.append((None, tokens[0].value[1:-1]))
			self.importEndIdx = self.importStmtIdx + 1

		if err:
			return []
		else:
			return pkgs
	
	def newImportBlock(self, pkgs):
		if len(pkgs) > 1:
			im = 'import (\n'
			for pkg in pkgs:
				if pkg[0] is None:
					im += '\t"%s"\n' % pkg[1]
				else:
					im += '\t%s "%s"\n' % (pkg[0], pkg[1])
			im += ')'
			return im
		elif len(pkgs) == 1:
			pkg = pkgs[0]
			if pkg[0] is None:
				return 'import "%s"' % pkg[1]
			else:
				return 'import %s "%s"' % (pkg[0], pkg[1])
		else:
			return ''

	def replacementRegion(self):
		start = self.tokens[self.importStmtIdx]
		end = self.tokens[self.importEndIdx]
		return sublime.Region(start.start, end.to)

	def pkgStmtLineRegion(self):
		for idx, tok in enumerate(self.tokens):
			if tok.kind == golex.IDENTIFIER and tok.value == 'package':
				return self.view.full_line(sublime.Region(tok.start, tok.to))

	def add_import(self, pkg):
		# Import statement is present
		if self.importStmtIdx != -1:
			pkgs = self.importedPkgs()
			# Check if this is already imported
			for name, importPath in pkgs:
				if importPath == pkg:
					return
			pkgs.append((None, pkg))
			pkgs.sort()
			replacementText = self.newImportBlock(pkgs)
			tx = self.view.begin_edit()
			self.view.replace(tx, self.replacementRegion(), replacementText)
			self.view.end_edit(tx)
		# No import statement present
		else:
			pkgs = ((None, pkg),)
			replacementText = '\n' + self.newImportBlock(pkgs) + '\n'
			# Find a package statement in the token list
			stmtLine = self.pkgStmtLineRegion()
			tx = self.view.begin_edit()
			self.view.insert(tx, stmtLine.b, replacementText)
			self.view.end_edit(tx)

	def remove_import(self, pkg):
		# Only attempt pkg removal if there's an import statement present.
		if self.importStmtIdx != -1:
			pkgs = self.importedPkgs()
			def remover(x): return x[1] != pkg
			pkgs = filter(remover, pkgs)
			pkgs.sort()
			replacementText = self.newImportBlock(pkgs)
			region = self.replacementRegion()
			if replacementText == '':
				# Check whether removing two lines is OK.
				# We deem it OK if the line just below the last part of the import
				# statement is empty. (We assume that there's a blank line on top
				# of the import statement and that this'll make the top blank line
				# the separator between the import block and what's below it.)
				region = self.view.full_line(self.view.full_line(region))
				lines = self.view.lines(region)
				# Not OK. Only remove the import line.
				if len(self.view.substr(lines[1])) != 0:
					region = self.view.full_line(self.replacementRegion())
			tx = self.view.begin_edit()
			self.view.replace(tx, region, replacementText)
			self.view.end_edit(tx)


class PromptGoImportCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Import:", "", self.on_done, None, None)
        pass

    def on_done(self, pkg):
        try:
            if self.window.active_view():
                self.window.active_view().run_command("go_import", {"pkg": pkg})
        except ValueError:
            pass

class PromptGoDropCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel("Drop import:", "", self.on_done, None, None)
        pass

    def on_done(self, pkg):
        try:
            if self.window.active_view():
                self.window.active_view().run_command("go_drop", {"pkg": pkg})
        except ValueError:
            pass


class GoImportCommand(sublime_plugin.TextCommand):
	def run(self, edit, pkg):
		im = ImportMutator(self.view)
		im.add_import(pkg)

class GoDropCommand(sublime_plugin.TextCommand):
	def run(self, edit, pkg):
		im = ImportMutator(self.view)
		im.remove_import(pkg)