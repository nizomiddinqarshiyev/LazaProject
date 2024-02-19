docker build -t <name> .
docker-compose build --up
docker-compose -f docker-compose.yml exec fastapi alembic revision --autogenerate -m "your commits"
docker-compose -f docker-compose.yml exec fastapi alembic upgrade head
