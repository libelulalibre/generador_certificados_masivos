from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from PyPDF2 import PdfReader, PdfWriter
import zipfile
import os
import io
from pathlib import Path

app = FastAPI(title="Generador Masivo de Certificados PDF")

# Configuración de directorios
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
CERTIFICADOS_DIR = BASE_DIR / "certificados_generados"

# Crear directorios si no existen
TEMPLATES_DIR.mkdir(exist_ok=True)
CERTIFICADOS_DIR.mkdir(exist_ok=True)

@app.post("/subir-archivos")
async def subir_archivos(
    template: UploadFile = File(..., description="Template (PDF)"),
    datos: UploadFile = File(..., description="Datos en Excel/CSV"),
):
    # Validar formato del template
    if not template.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El template debe ser un PDF")

    # Guardar archivos
    template_path = TEMPLATES_DIR / template.filename
    datos_path = TEMPLATES_DIR / datos.filename

    with open(template_path, "wb") as buffer:
        buffer.write(await template.read())
    with open(datos_path, "wb") as buffer:
        buffer.write(await datos.read())

    return {
        "mensaje": "Archivos subidos correctamente",
        "template": template.filename,
        "datos": datos.filename
    }

@app.post("/generar-certificados")
async def generar_certificados(
    template_nombre: str,
    datos_nombre: str,
    campo_nombre: str = "nombre",
    x: int = 100,
    y: int = 100,
    color_texto: str = "#000000",  # Negro por defecto (formato HEX)
    tamano_fuente: int = 12,
):
    """
    Genera certificados PDF en masa.
    Parámetros:
    - x, y: Posición del texto en puntos (1 punto = 1/72 pulgadas)
    - color_texto: Código HEX (ej: "#FF0000" para rojo)
    """
    # Validar template PDF
    template_path = TEMPLATES_DIR / template_nombre
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template no encontrado")
    if not template_nombre.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El template debe ser PDF")

    # Cargar datos
    datos_path = TEMPLATES_DIR / datos_nombre
    try:
        if datos_nombre.endswith('.csv'):
            df = pd.read_csv(datos_path)
        else:
            df = pd.read_excel(datos_path, engine='openpyxl')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al leer datos: {str(e)}")

    # Procesar cada certificado
    zip_path = CERTIFICADOS_DIR / "certificados.zip"
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for _, row in df.iterrows():
                nombre = str(row[campo_nombre])
                output_path = CERTIFICADOS_DIR / f"certificado_{nombre}.pdf"

                # 1. Crear PDF temporal con el texto dinámico
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.setFont("Helvetica", tamano_fuente)
                can.setFillColor(HexColor(color_texto))
                can.drawString(x, y, nombre)  # Posición en puntos
                can.save()

                # 2. Combinar con el template PDF
                template_pdf = PdfReader(template_path)
                texto_pdf = PdfReader(packet)
                output = PdfWriter()

                page = template_pdf.pages[0]
                page.merge_page(texto_pdf.pages[0])
                output.add_page(page)

                with open(output_path, "wb") as f:
                    output.write(f)

                zipf.write(output_path, output_path.name)
                os.remove(output_path)  # Limpiar temporal

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="certificados.zip"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")