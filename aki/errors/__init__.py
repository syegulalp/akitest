class ReloadException(Exception):
    pass


class QuitException(Exception):
    pass


class AkiBaseException(Exception):
    def __init__(self, txt, node, err=None):
        self.txt = txt
        self.node = node
        self.err = err

    @property
    def err_type(self):
        return self.__class__.__name__[3:]

    def __str__(self):
        lines = self.txt.split()
        line = self.node.line - 1
        return f"{self.err_type}: (line {self.node.line}, col {self.node.column}) {self.err}\n{lines[line]}\n{'-'*(self.node.column-1)}^"


class AkiSyntaxError(AkiBaseException):
    pass


class AkiTypeError(AkiBaseException):
    pass


class AkiNameError(AkiBaseException):
    pass
