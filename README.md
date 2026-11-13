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

## Demonstracja przejazdu kolejowego

Można wygenerować pięć syntetycznych klatek z samochodem, wykryć jego położenie kolorem,
oszacować prędkość z przesunięcia między klatkami i otrzymać przykładowy dystans hamowania:

```sh
python -m app.crossing_demo --output-dir examples/crossing_demo
```

Wynikiem są pięć klatek z przekroczeniem limitu w katalogu głównym oraz pięć klatek bez
przekroczenia w `within_limit/`; każda sekwencja ma własne `summary.json`. Scena oraz detektor
są sztuczne;
pojedyncze zdjęcie nie wystarcza do pomiaru prędkości. Wynik dystansu (około 638 m dla
założeń widocznych w JSON: 80 km/h, 0,5 m/s², 2 s i 100 m marginesu) jest wyłącznie
ilustracją wzoru, a nie zaleceniem ani gwarancją bezpiecznej odległości. Nie używać do
sterowania pociągiem. Rzeczywista ochrona przejazdu wymaga zatwierdzonego systemu kolejowego,
kalibracji i parametrów hamowania potwierdzonych dla konkretnego składu i toru.

## Docker

```sh
docker build --target runtime -t opencv-edge-mvp .
docker run --rm -v "$(pwd)/examples:/input:ro" -v "$(pwd):/output" \
  opencv-edge-mvp /input/shapes.pgm --output /output/edges.png
```

The crossing demo is also available in the runtime image. Mount `examples` as writable
output and override the default Canny entrypoint:

PowerShell (Windows):

```powershell
docker run --rm -v "${PWD}/examples:/output" --entrypoint python opencv-edge-mvp -m app.crossing_demo --output-dir /output/crossing_demo
```

Bash (Linux/macOS):

```sh
docker run --rm -v "$(pwd)/examples:/output" --entrypoint python opencv-edge-mvp \
  -m app.crossing_demo --output-dir /output/crossing_demo
```

PowerShell odpowiednik wolumenów: `-v "${PWD}/examples:/input:ro" -v "${PWD}:/output"`.

## Testy

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q --junitxml=junit.xml
```

Testy jednostkowe sprawdzają detektor i walidację parametrów. Integracyjne uruchamiają
pełny przepływ plikowy oraz CLI na przykładowym obrazie.
Raport JUnit zapisuje się jako `junit.xml`.

## Jenkins

Pipeline wymaga agenta z etykietą `docker`, dostępem do demona Docker i checkoutem repozytorium.
Buduje target `test`, uruchamia testy w kontenerze, a potem buduje obraz `runtime`.
Obie wersje współdzielą warstwę zależności, co skraca kompilację i korzysta z cache Dockera.
Jenkins publikuje raport JUnit również wtedy, gdy testy zakończą się błędem. Obraz wynikowy
pozostaje lokalnie na agencie; publikowanie do rejestru można dodać przez credentials.

## Kontrola QA

Zobacz [QA_GUIDE.md](QA_GUIDE.md), gdzie są przypadki do ręcznego sprawdzenia, kryteria akceptacji,
mapa testów i szablon zgłoszenia błędu.
