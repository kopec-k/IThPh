# Projekt Fizyka Teoretyczna
## Cele projektu

Dwuwymiarowa symulacja fizyki w czasie rzeczywistym, która generuje solver równań ruchu "w locie" względem zadanego w składni kodu SymPy Lagranżjanu

Zaimplementowane "Dodatkowe cele":

* wczytywanie Lagranżjanu ze standardowego wejścia lub pliku;
* wczytywanie transformacji wsp. uogólnione <-> kartezjańskie;
* zrównoleglenie metody Rungego-Kutty przy pomocy OpenMP;

## Uruchamianie

Z katalogu `run` należy wykonać:

```bash
python particles.py <plik_wejściowy>
```

Przykład:

```bash
python particles.py simulations/lissajous.txt
```

## Przykładowe symulacje

W katalogu `run/simulations`:

* `elastic_pendulum.txt` – wahadło na sprężynie,
* `gravity.txt` – układ trzech satelitów orbitujących wokół wspólnego środka masy,
* `harmonic.txt` – oscylator harmoniczny,
* `lissajous.txt` – anizotropowy oscylator harmoniczny.