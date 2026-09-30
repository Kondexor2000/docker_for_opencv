# OpenCV Edge MVP

Mała aplikacja Python, która wczytuje obraz i zapisuje mapę krawędzi Canny.
Obrazy wejściowe są kolorowe lub w odcieniach szarości; wynik jest jednokanałowym PNG.

## Szybki start lokalny

Python 3.12+:

```sh
python -m venv .venv
# Linux/macOS: . .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m app examples/shapes.pgm --output output.png
```

Instalacja OpenCV headless nie wymaga graficznego GUI i jest odpowiednia dla kontenerów.
Warstwy Dockera instalują zależności przed kodem, więc zmiana kodu nie unieważnia cache pip.

## Docker

```sh
docker build --target runtime -t opencv-edge-mvp .
docker run --rm -v "$(pwd)/examples:/input:ro" -v "$(pwd):/output" \
  opencv-edge-mvp /input/shapes.pgm --output /output/edges.png
```

PowerShell odpowiednik wolumenów: `-v "${PWD}/examples:/input:ro" -v "${PWD}:/output"`.

## Testy

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Testy jednostkowe sprawdzają detektor i walidację parametrów. Integracyjne uruchamiają
pełny przepływ plikowy oraz CLI na przykładowym obrazie.

## Jenkins

Pipeline wymaga agenta z etykietą `docker`, dostępem do demona Docker i checkoutem repozytorium.
Buduje target `test`, uruchamia testy w kontenerze, a potem buduje obraz `runtime`.
Obie wersje współdzielą warstwę zależności, co skraca kompilację i korzysta z cache Dockera.
Obraz wynikowy pozostaje lokalnie na agencie; publikowanie do rejestru można dodać przez credentials.
