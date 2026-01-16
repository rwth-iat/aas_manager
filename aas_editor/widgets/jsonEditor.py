#  Copyright (C) 2025  Igor Garmaev, garmaev@gmx.net
#
#  This program is made available under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
#  A copy of the GNU General Public License is available at http://www.gnu.org/licenses/
from PyQt6.Qsci import QsciScintilla, QsciLexerJSON
from PyQt6.QtGui import QColor


class JSONEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. Set the Lexer (Syntax Highlighting)
        # QScintilla has a built-in JSON lexer
        self.lexer = QsciLexerJSON()
        #self.lexer.setDefaultFont(QFont("Consolas", 10))
        self.setLexer(self.lexer)

        # 2. Line Numbers (Margin 0)
        # We tell it to display numbers in the first margin
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000") # Initial width for 4 digits
        self.setMarginsForegroundColor(QColor("#888888"))

        # 3. Indentation & Tabs
        self.setTabWidth(2)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)

        # 4. Brace Matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        # 5. Folding (Optional - allows collapsing objects)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        #self.setMarginWidth(1, 0)  # Hide marker margin if you don't want it

        # 6. Caret (Cursor) Color
        self.setCaretForegroundColor(QColor("white"))

        self.apply_dark_theme()


    def apply_dark_theme(self):
        # 1. Set Main Editor Colors
        self.setColor(QColor("#abb2bf"))  # Default Text Color (Light Grey)
        self.setPaper(QColor("#282c34"))  # Background Color (Dark Grey)
        self.setCaretForegroundColor(QColor("white"))  # Cursor Color

        # 2. Set Margin (Line Number) Colors
        self.setMarginsBackgroundColor(QColor("#282c34"))
        self.setMarginsForegroundColor(QColor("#5c6370"))  # Line Number Color

        # 3. Configure Lexer Styles (JSON specific)
        # Get the lexer (assuming self.lexer is already set)
        lexer = self.lexer

        # Set default background for all styles to match editor
        lexer.setDefaultPaper(QColor("#282c34"))
        lexer.setDefaultColor(QColor("#abb2bf"))

        # Define a helper to keep code clean
        def set_style(style_id, color_hex, bold=False):
            color = QColor(color_hex)
            lexer.setColor(color, style_id)
            lexer.setPaper(QColor("#282c34"), style_id)  # Ensure background matches
            if bold:
                font = lexer.font(style_id)
                font.setBold(True)
                lexer.setFont(font, style_id)

        # --- JSON Syntax Colors (VS Code / One Dark inspired) ---

        # Numbers (e.g. 123, 4.56) -> Orange/Dark Yellow
        set_style(QsciLexerJSON.Number, "#d19a66")

        # Strings (e.g. "value") -> Green
        set_style(QsciLexerJSON.String, "#98c379")

        # Property Names (e.g. "key": ) -> Red/Pink
        # Note: QScintilla's JSON lexer sometimes groups keys as 'String' or 'Property'.
        # usually, 'Property' is the key.
        set_style(QsciLexerJSON.Property, "#e06c75")

        # Keywords (true, false, null) -> Blue/Cyan
        set_style(QsciLexerJSON.Keyword, "#56b6c2", bold=True)

        # Operators ({ } [ ] : ,) -> Light Grey/White
        set_style(QsciLexerJSON.Operator, "#abb2bf")

        # Comments (if you allow comments in JSON5) -> Grey Italics
        set_style(QsciLexerJSON.CommentBlock, "#7f848e")
        set_style(QsciLexerJSON.CommentLine, "#7f848e")

        # 6. Set Folding Colors (optional, for dark mode visibility)
        # Background color for the folding margin
        self.setFoldMarginColors(QColor("#282c34"), QColor("#abb2bf"))
