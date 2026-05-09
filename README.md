# notify-mesh
Manage, route and control notifications across multiple providers from a single platform.

## Getting Started

**Prerequisites:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

1. Clone the repo and enter the directory:
   ```bash
   git clone <repo-url>
   cd notify-mesh
   ```

2. Install dependencies:
   ```bash
   uv sync --extra dev
   ```

3. Start the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

