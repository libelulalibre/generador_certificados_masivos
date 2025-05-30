# generador_certificados_masivos
Programa destinado a la emisión masiva de certificados a partir de la carga de un template y base de datos correspondiente.

# Generador de Certificados Masivos

Herramienta para generar certificados personalizados en formato `.docx` a partir de una plantilla y datos en Excel.

## 📋 Requisitos
- Python 3.8+
- Librerías: `pandas`, `python-docx`

## 🔧 Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/libelulalibre/generador_certificados_masivos.git
2. pip install -r requirements.txt


#### **4. Uso**
```markdown
## 🚀 Uso
1. Prepara tus datos:
   - Archivo Excel (`inscritos.xlsx`) con columnas `NOMBRE` y `APELLIDO`.
   - Plantilla Word (`template.docx`) con placeholders como `{{NOMBRE}}` y `{{APELLIDO}}`.
2. Ejecuta el generador:
   ```bash
   python generador.py

   
#### **5. Estructura del Proyecto**
```markdown
## 📂 Estructura
generador_certificados_masivos/
├── generador.py          # Script principal
├── template.docx         # Plantilla de certificado
├── inscritos.xlsx        # Datos de participantes
├── certificados/         # (Se crea al ejecutar) Certificados generados
└── README.md             # Documentación

## ⚙️ Configuración
Modifica el archivo `generador.py` para cambiar:
- Nombres de columnas (líneas que usan `row["NOMBRE"]`).
- Ruta de salida (busca `certificados/` en el código).