import sys, os
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from minhas_funcoes import fatorial

def test_fatorial_de_zero():
    assert fatorial(0) == 1
    
def test_fatorial_de_um():
    assert fatorial(1) == 1

def test_fatorial_de_cinco():
    assert fatorial(5) == 120

def test_fatorial_numero_negativo():
    with pytest.raises(ValueError):
        fatorial(-3)
        