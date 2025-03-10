#!/bin/bash
docker compose pull
docker compose up -d

sleep 5

case "$(uname -s)" in
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        # Windows environment
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
        echo "Please open the URLs manually: http://localhost:8001/docs and http://localhost:8025"
        ;;
esac

trap "echo 'Beende Container...'; docker compose down" EXIT

docker compose logs -f
