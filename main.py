from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import zipfile
import os
from pathlib import Path

app = FastAPI(title="Generador Masivo de Certificados")

# Configuración de directorios
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
CERTIFICADOS_DIR = BASE_DIR / "certificados_generados"

# Crear directorios si no existen
TEMPLATES_DIR.mkdir(exist_ok=True)
CERTIFICADOS_DIR.mkdir(exist_ok=True)

@app.post("/subir-archivos")
async def subir_archivos(
    template: UploadFile = File(..., description="Template (PNG/JPG)"),
    datos: UploadFile = File(..., description="Datos en Excel/CSV"),
):
    # Guardar template
    template_path = TEMPLATES_DIR / template.filename
    with open(template_path, "wb") as buffer:
        buffer.write(await template.read())

    # Guardar datos
    datos_path = TEMPLATES_DIR / datos.filename
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
    color_texto: str = "black",
    tamano_fuente: int = 30,
):
    """
    Genera certificados en masa basados en un template y datos de usuarios.
    Parámetros:
    - template_nombre: Nombre del archivo template (debe estar en /templates)
    - datos_nombre: Nombre del archivo con datos (Excel/CSV)
    - campo_nombre: Columna que contiene los nombres a insertar
    - x, y: Posición del texto en píxeles
    - color_texto: Color del texto (ej: "black", "#FF0000")
    - tamano_fuente: Tamaño de fuente en puntos
    """
    # Validar formato de imagen
    if not template_nombre.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(
            status_code=400,
            detail="Formato de imagen no soportado. Use PNG, JPG o JPEG"
        )

    # Cargar datos
    datos_path = TEMPLATES_DIR / datos_nombre
    try:
        if datos_nombre.endswith('.csv'):
            df = pd.read_csv(datos_path)
        else:
            df = pd.read_excel(datos_path, engine='openpyxl')
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al leer archivo de datos: {str(e)}"
        )

    # Verificar existencia del template
    template_path = TEMPLATES_DIR / template_nombre
    if not template_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Archivo template no encontrado"
        )

    # Generar certificados
    zip_path = CERTIFICADOS_DIR / "certificados.zip"
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for _, row in df.iterrows():
                try:
                    nombre = str(row[campo_nombre])
                    with Image.open(template_path) as img:
                        draw = ImageDraw.Draw(img)
                        
                        # Configurar fuente (manejo de fallback)
                        try:
                            font = ImageFont.truetype("arial.ttf", tamano_fuente)
                        except:
                            font = ImageFont.load_default()
                        
                        draw.text((x, y), nombre, fill=color_texto, font=font)

                        cert_path = CERTIFICADOS_DIR / f"certificado_{nombre}.png"
                        img.save(cert_path)
                        zipf.write(cert_path, cert_path.name)
                        os.remove(cert_path)  # Limpiar archivo temporal
                
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error al generar certificado para {nombre}: {str(e)}"
                    )

        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="certificados.zip"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear archivo ZIP: {str(e)}"
        )