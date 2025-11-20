# SDN Attack Simulator

## Instalación

```bash
git clone https://github.com/FleitasEzequiel/sdn-simulador.git
cd sdn-simulador
uv sync
```

## Ejecución

### Interfaz Web (Recomendado)
```bash
.venv\Scripts\Activate.ps1
uvicorn app:app --reload
```
Abrir en navegador: http://localhost:8000

### CLI
```bash
.venv\Scripts\Activate
python main.py
```