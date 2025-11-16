import os
import shutil


def _worktempdir() -> str:
    """Zwraca ścieżkę do katalogu tymczasowego SDK KSeF."""
    dir = os.path.join(os.path.dirname(__file__), "..", "worktemp")
    os.makedirs(dir, exist_ok=True)
    return dir


def _patterndir(patt: str) -> str:
    """Zwraca ścieżkę do katalogu ze wzorcami dokumentów KSeF."""
    dir = os.path.join(os.path.dirname(__file__), "..", "testdata")
    return os.path.join(dir, patt)


class KONWDOKUMENT:

    @staticmethod
    def zrob_dokument_xml(zmienne: dict) -> str:
        """Generuje XML dokumentu KSeF na podstawie słownika zmienn."""
        sou = _patterndir("FA_3_Przykład_9.xml")
        dest = os.path.join(_worktempdir(), "dokument_ksef.xml")
        shutil.copyfile(sou, dest)
        return dest
