# Busca en todos los PDF de una carpeta y sus subcarpetas las oraciones que contienen ciertas palabras
# Si no se indica el directorio (primer argumento), la búsqueda se efectúa en la ubicación actual
# La función activa y desactiva un entorno virtual de Python (donde está instalada la librería PyMuPDF):
 
buscar() {
	if [ -d "$1" ]; then
		source /ruta_a_entorno/venv/bin/activate && python /ubicación/buscador.py $@ && deactivate
	else
		source /ruta_a_entorno/venv/bin/activate && python /ubicación/buscador.py "$(pwd)" $@ && deactivate
	fi
}

# Ejemplo: $ buscar [/ruta] palabra1 palabra2 palabra3