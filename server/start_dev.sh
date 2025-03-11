#!/bin/bash
docker compose pull
docker compose up -d

sleep 5

case "$(uname -s)" in
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        # Windows-Umgebung
        start "http://localhost:8001/docs"
        start "http://localhost:8025"
        ;;
    Darwin*)
        open "http://localhost:8001/docs"
        open "http://localhost:8025"
        ;;
    Linux*)
        xdg-open "http://localhost:8001/docs"
        xdg-open "http://localhost:8025"
        ;;
    *)
        echo "Bitte öffne die URLs manuell: http://localhost:8001/docs und http://localhost:8025"
        ;;
esac

trap "echo 'Beende Container...'; docker compose down" EXIT

docker compose logs -f backend
