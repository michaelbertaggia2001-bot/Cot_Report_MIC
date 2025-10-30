# -*- coding: utf-8 -*-
"""Utility robuste per encoding UTF-8 e output su file su Windows.

Risolve il problema della "mutazione genetica" tra console e clipboard
scrivendo direttamente su file UTF-8 con BOM per massima compatibilità.

Questo modulo estende encoding_fix.py con funzionalità avanzate per output
affidabile che può essere copiato/incollato senza mutazioni di caratteri.
"""

from __future__ import annotations

import sys
import io
from pathlib import Path
from typing import Optional
import unicodedata


def force_utf8_stdout() -> None:
    """Forza stdout/stderr a UTF-8. Utile ma non risolve copia/incolla.
    
    Questa funzione configura stdout e stderr per usare UTF-8 encoding,
    risolvendo problemi di visualizzazione caratteri su Windows dove
    l'encoding di default è cp1252.
    """
    if sys.version_info >= (3, 7):
        try:
            # Python 3.7+: usa reconfigure (metodo preferito)
            sys.stdout.reconfigure(encoding='utf-8', errors='replace', newline='\n')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace', newline='\n')
        except (AttributeError, ValueError, OSError):
            # Fallback se reconfigure non disponibile o fallisce
            _setup_utf8_encoding_fallback()
    else:
        # Python < 3.7: usa wrapper
        _setup_utf8_encoding_fallback()


def _setup_utf8_encoding_fallback() -> None:
    """Fallback per configurare UTF-8 usando TextIOWrapper."""
    # Solo se non è già un TextIOWrapper con UTF-8
    if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding='utf-8',
                errors='replace',
                newline='\n',
                line_buffering=True
            )
        except Exception:
            pass  # Fallback silenzioso se non possibile
    
    if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding != 'utf-8':
        try:
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding='utf-8',
                errors='replace',
                newline='\n',
                line_buffering=True
            )
        except Exception:
            pass  # Fallback silenzioso se non possibile


def sanitize_ascii(text: str) -> str:
    """Conserva solo ASCII stampabile, rimuovendo caratteri non ASCII.
    
    Args:
        text: Stringa da sanificare
        
    Returns:
        Stringa contenente solo caratteri ASCII stampabili
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Rimuovi BOM e caratteri invisibili
    text = text.replace('\ufeff', '').replace('\u200b', '').replace('\u200c', '').replace('\u200d', '')
    
    # Normalizza Unicode
    normalized = unicodedata.normalize("NFKD", text)
    
    # Rimuovi caratteri di controllo (0x00-0x1F eccetto tab, newline, carriage return)
    cleaned = ''.join(c for c in normalized if ord(c) < 128 or c in '\t\n\r')
    
    # Converte in ASCII puro (rimuove caratteri non ASCII)
    result = cleaned.encode("ascii", "ignore").decode("ascii")
    
    # Rimuovi eventuali spazi multipli o caratteri strani rimasti
    result = ''.join(c if ord(c) < 128 and (c.isprintable() or c in '\t\n\r') else ' ' for c in result)
    
    return result


def safe_print(text: str = "",
               *,
               ascii_only: bool = False,
               tee_file_utf8: Optional[str] = None,
               tee_file_ascii: Optional[str] = None,
               copy_to_clipboard: bool = False) -> None:
    """
    Stampa (opzionale) e scrive su file in modo affidabile.
    
    Args:
        text: Testo da stampare/scrivere
        ascii_only: Se True, stampa solo ASCII sanificato in console
        tee_file_utf8: Path file UTF-8 con BOM (massima compatibilità Windows)
        tee_file_ascii: Path file solo ASCII (per debug)
        copy_to_clipboard: Se True, tenta di copiare in clipboard (richiede pyperclip)
    
    IMPORTANTE: Per copiare/incollare senza mutazioni, usa il file UTF-8.
    Il testo nel file UTF-8 è preservato integralmente senza sanificazione.
    """
    # Prepara il testo per console (ASCII se richiesto)
    console_text = sanitize_ascii(text) if ascii_only else text
    
    # Stampa "di cortesia": non affidarti a questo per il copia/incolla.
    print(console_text, flush=True)
    
    # Scrittura su file UTF-8 con BOM (perfetto per copia/incolla)
    if tee_file_utf8:
        try:
            # Crea directory se necessario
            file_path = Path(tee_file_utf8)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # BOM (utf-8-sig) per compatibilità con vecchie app che non rilevano UTF-8
            with open(tee_file_utf8, 'a', encoding='utf-8-sig', errors='replace', newline='\n') as f:
                f.write(text + '\n')  # scrivi il testo intero, non sanificato
        except Exception:
            pass  # Fallback silenzioso se non possibile scrivere file
    
    # Scrittura su file ASCII (per debug/diff)
    if tee_file_ascii:
        try:
            # Crea directory se necessario
            file_path = Path(tee_file_ascii)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(tee_file_ascii, 'a', encoding='ascii', errors='backslashreplace', newline='\n') as f:
                f.write(text + '\n')
        except Exception:
            pass  # Fallback silenzioso se non possibile scrivere file
    
    # Copia in clipboard (opzionale, richiede pyperclip)
    if copy_to_clipboard:
        try:
            import pyperclip
            pyperclip.copy(text)  # Copia il testo UTF-8 originale, non sanificato
        except ImportError:
            pass  # Silenzioso se pyperclip non disponibile
        except Exception:
            pass  # Fallback silenzioso in caso di errori


# Backward compatibility: alias per codice esistente
setup_utf8_encoding = force_utf8_stdout

