# Copyright (c) 2011 Mikkel Krautz
# The use of this source code is goverened by a BSD-style
# license that can be found in the LICENSE-file.

from __future__ import unicode_literals


IDENTIFIER   = 'IDENTIFIER'
STRINGLIT    = 'STRINGLIT'
SEMICOLON    = 'SEMICOLON'
LINECOMMENT  = 'LINECOMMENT'
MULTICOMMENT = 'MULTICOMMENT'
LPAREN       = 'LPAREN'
RPAREN       = 'RPAREN'


class Token(object):
		def __init__(self, lexer, kind, start, to):
			self.lexer = lexer
			self.kind = kind
			self.start = start
			self.to = to

		def __repr__(self):
			return '<Token %s; %s (%i,%i)>' % (self.kind,
			                                   self.lexer.str[self.start:self.to],
			                                   self.start, self.to)

		@property
		def value(self):
			return self.lexer.str[self.start:self.to]			            


class Lexer(object):
	'''
		Lexer is a simple lexer for the subset of the
		Go language needed to add and drop import statements
		from a source file.
	'''
		
	def __init__(self, str):
		self.str = str
		self.pos = 0
		self.tokens = []
		pass

	# Return a string with n chars of lookahead
	def lookahead(self, n=1):
		return self.str[self.pos:self.pos+n]

	def lex(self):
		while True:
			c = self.lookahead(2)
			# eof check
			if len(c) == 0:
				break
			# identifiers
			if c[0].isalpha():
				tokens = self.scanIdentifier()
				continue
			# string literals
			elif c[0] == '"':
				tokens = self.scanStringLiteral()
			# semicolon
			elif c[0] == ';':
				tokens = self.scanSemiColon()
			# single-line comments
			elif c == '//':
				tokens = self.scanLineComment()
			# multi-comments
			elif c == '/*':
				tokens = self.scanMultiComment()
			# lparen
			elif c[0] == '(':
				tokens = self.scanLeftParen()
			# rparen
			elif c[0] == ')':
				tokens = self.scanRightParen()
			# consume unknowns
			else:
				self.getch()

	def accept(self, chars):
		ch = self.getch()
		if not ch in chars:
			self.reject('expected one of %s' % chars)

	def reject(self, msg):
		raise Exception('reject! %s' % msg)
	
	def newToken(self, kind, start, to):
		self.tokens.append(Token(self, kind, start, to))

	def getch(self):
		ch = self.str[self.pos]
		self.pos += 1
		return ch

	def putch(self, ch):
		self.pos -= 1

	# scan an identifier
	def scanIdentifier(self):
		start = self.pos
		ch = self.getch()
		if not ch.isalpha():
			self.reject('expected alpha')
		while True:
			ch = self.getch()
			if not ch.isalnum():
				self.putch(ch)
				break
		self.newToken(IDENTIFIER, start, self.pos)
	
	# scan string literal
	def scanStringLiteral(self):
		start = self.pos
		self.accept('"')
		while True:
			ch = self.getch()
			if ch == '"':
				break
			if ch == '\n':
				self.reject('expected terminating "')
		self.newToken(STRINGLIT, start, self.pos)

	# scan semicolon
	def scanSemiColon(self):
		start = self.pos
		self.accept(';')
		self.newToken(SEMICOLON, start, self.pos)

	# scan line comment
	def scanLineComment(self):
		start = self.pos
		self.accept('/')
		self.accept('/')
		while True:
			ch = self.getch()
			if ch == '\n':
				break
		self.newToken(LINECOMMENT, start, self.pos)

	# scan a multi comment
	def scanMultiComment(self):
		start = self.pos
		self.accept('/')
		self.accept('*')
		while True:
			ch = self.getch()
			if ch == '*':
				break
		self.accept('/')
		self.newToken(MULTICOMMENT, start, self.pos)

	# scan lparen
	def scanLeftParen(self):
		start = self.pos
		self.accept('(')
		self.newToken(LPAREN, start, self.pos)

	# scan rparen
	def scanRightParen(self):
		start = self.pos
		self.accept(')')
		self.newToken(RPAREN, start, self.pos)
	
if __name__ == '__main__':
	go = '''
// Package main implements stuff
package main

import (
	"hey"
	"ho"
)

func name(name string) string {
	return "hello there, " + name + "!"
}
'''
	l = Lexer(go)
	l.lex()
	print l.tokens