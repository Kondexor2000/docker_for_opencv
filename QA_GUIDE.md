# Przewodnik QA

## Cel i kryteria akceptacji

MVP przyjmuje lokalny obraz, wykrywa krawędzie Canny i zapisuje mapę krawędzi jako PNG.

- Dla poprawnego obrazu CLI kończy się kodem `0`, tworzy niepusty plik wynikowy i wypisuje JSON
  z wymiarami, liczbą pikseli krawędzi oraz ścieżką wyniku.
- Obraz wyjściowy jest jednokanałowy, ma te same wymiary co wejście i zawiera krawędzie dla
  przykładowych figur.
- Brak lub uszkodzony obraz zgłasza czytelny komunikat i kończy się niezerowym kodem.
- Niepoprawne progi Canny zgłaszają `ValueError`.
- Testy jednostkowe i integracyjne przechodzą lokalnie i w Jenkinsie; Jenkins publikuje JUnit.

## Uruchomienie

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q --junitxml=junit.xml
```

Wynik obrazu można obejrzeć po przetworzeniu fixture’a:

```sh
python -m app examples/shapes.pgm --output output.png
```

Oczekiwany rozmiar `output.png`: 160×120, skala szarości. Drugi fixture to
`examples/checkerboard.pgm` (96×96). Przykłady są zapisane jako PGM ASCII, więc łatwo je
przeglądać i nie wymagają zewnętrznego pobierania danych.

## Przypadki ręczne

| ID | Przypadek | Kroki | Oczekiwany wynik |
|---|---|---|---|
| QA-01 | Kształty | Uruchom CLI na `examples/shapes.pgm` | PNG 160×120; widoczne krawędzie prostokąta i koła |
| QA-02 | Szachownica | Uruchom CLI na `examples/checkerboard.pgm` | PNG 96×96; krawędzie pól są widoczne |
| QA-03 | Inny format nazwy wyjściowej | Użyj `--output work/review.png` | Katalog jest tworzony, plik zapisany poprawnie |
| QA-04 | Brak wejścia | Podaj nieistniejący plik | Niezerowy kod i komunikat `Could not read image` |
| QA-05 | Domyślne wyjście | Uruchom z samą ścieżką wejściową w pustym katalogu | Powstaje `output.png` |
| QA-06 | Kontener | Zbuduj target `runtime` i przetwórz fixture zamontowany jako wolumen | Kontener kończy się kodem `0`, zapisuje PNG w zamontowanym katalogu |

## Automatyczna mapa pokrycia

- `tests/test_processor.py`: detekcja, kształt i typ wyniku, walidacja progów oraz zapis pliku.
- `tests/test_cli.py`: CLI end-to-end na fixture’ach i zachowanie dla brakującego wejścia.
- `Jenkinsfile`: budowa obrazu testowego, testy w kontenerze, raport JUnit i budowa obrazu runtime.

## Szablon zgłoszenia błędu

```text
Tytuł:
ID przypadku QA:
Środowisko (Python/Docker, system):
Kroki odtworzenia:
Oczekiwany wynik:
Rzeczywisty wynik:
Kod wyjścia / fragment logu:
Załącznik (obraz wejściowy lub wynikowy):
```
