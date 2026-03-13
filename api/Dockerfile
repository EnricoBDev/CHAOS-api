FROM astral/uv:trixie-slim

WORKDIR /app

COPY . /app 

# install openssl and remove cached apt lists
RUN apt update && apt install -y openssl && rm -rf /var/lib/apt/lists/*

RUN echo "\nSECRET=$(openssl rand -hex 32)" >> .env

ENV UV_NO_DEV=1 
ENV UV_COMPILE_BYTECODE=1

RUN uv sync --locked

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]