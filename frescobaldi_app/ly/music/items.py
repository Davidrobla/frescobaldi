# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2014 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
The items a read music expression is constructed with.

Whitespace is left out, but comments are retained.

"""

from __future__ import unicode_literals


import node

import ly.lex.lilypond


class Item(node.WeakNode):
    """Represents any item in the music of a document.
    
    This can be just a token, or an interpreted construct such as a note,
    rest or sequential or simultanuous construct , etc.
    
    Some Item instances just have one responsible token, but others have a
    list or tuple to tokens.
    
    An Item also has a pointer to the Document it originates from.
    
    """
    document = None
    tokens = ()
    token = None


class Token(Item):
    """Any token that is not otherwise recognized""" 


class Container(Item):
    """An item having a list of child items."""


class Duration(Item):
    """A duration"""
    
    
class Durable(Item):
    """An Item that has a Duration attribute."""
    duration = None
    

class Chord(Durable, Container):
    pass


class Note(Durable):
    """A Note that has a ly.pitch.Pitch"""
    pitch = None


class Skip(Durable):
    pass


class Rest(Durable):
    pass


class Music(Container):
    simultaneous = False
    """A music expression, either << >> or { }."""


class SchemeValue(Item):
    """The full list of tokens after a #."""
    

class StringValue(Item):
    """A double-quoted string."""


class Comment(Item):
    """A comment."""
    


def consume(source):
    """Yield the tokens until a parser is exit."""
    depth = source.state.depth()
    for t in source:
        yield t
        if source.state.depth() < depth:
            break

def read(source):
    """Yield Item instances reading from source."""
    for t in source:
        c = t.__class__
        if c == ly.lex.lilypond.SchemeStart:
            item = SchemeValue()
            item.token = t
            item.tokens = tuple(consume(source))
            yield item
        elif issubclass(c, ly.lex.BlockCommentStart):
            item = Comment()
            item.token = t
            item.tokens = tuple(consume(source))
            yield item
        elif issubclass(c, ly.lex.Comment):
            item = Comment()
            item.token = t
            yield item
        elif issubclass(c, ly.lex.StringStart):
            item = StringValue()
            item.token = t
            item.tokens = tuple(consume(source))
            item.value = ''.join(
                t[1:] if isinstance(t, ly.lex.Character) and t.startswith('\\') else t
                for t in item.tokens[:-1])
            yield item
        