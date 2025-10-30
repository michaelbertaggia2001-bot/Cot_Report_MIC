# -*- coding: utf-8 -*-
"""Utility per fixare encoding UTF-8 su stdout/stderr su Windows.

Questo modulo fornisce una funzione per configurare correttamente l'encoding
di stdout e stderr a UTF-8, risolvendo problemi di visualizzazione caratteri
su Windows dove l'encoding di default è cp1252.
"""
import sys


def setup_utf8_encoding():
    """Configura stdout e stderr per usare UTF-8 encoding.
    
    Su Windows, Python usa cp1252 di default per stdout/stderr, causando
    problemi di visualizzazione con caratteri non ASCII. Questa funzione
    forza UTF-8 per risolvere il problema.
    
    Compatibile con Python 3.7+ (usa reconfigure) e versioni precedenti
    (usa TextIOWrapper).
    """
    if sys.version_info >= (3, 7):
        try:
            # Python 3.7+: usa reconfigure (metodo preferito)
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError, OSError):
            # Fallback se reconfigure non disponibile o fallisce
            _setup_utf8_encoding_fallback()
    else:
        # Python < 3 Benefits: usa wrapper
        _setup_utf8_encoding_fallback()


def _setup_utf8_encoding_fallback():
    """Fallback per configurare UTF-8 usando TextIOWrapper."""
    import io
    
    # Solo se non è già un TextIOWrapper con UTF-8
    if hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, 
            encoding='utf-8', 
            errors='replace',
            line_buffering=sys.stdout.line_buffering
        )
    
    if hasattr(sys.stderr, 'buffer') and sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, 
            encoding='utf-8', 
            errors='replace',
            line_buffering=sys.stderr.line_buffering
        )

