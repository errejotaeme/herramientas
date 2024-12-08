import argparse
import fitz
import timeit
from pathlib import Path

# Recibe como primer argumento la carpeta con los PDF en los que se quiere encontrar 
# las oraciones que contienen ciertas palabras. 
# Cada una de ellas se ingresan separadas por coma.
# Exporta el resultado de la busqueda a la misma carpeta que recibe como entrada.
def buscar(carpeta:str, palabras:str):
    instancia_busqueda = Busqueda(carpeta, palabras)
    del instancia_busqueda


class Busqueda:

    # Diccionario con los datos necesarios para realizar la búsqueda
    requisitos = {}

    def __init__(self, directorio:str, palabras):
        # Define las rutas donde se va a trabajar
        if directorio.endswith('/'):
            self.requisitos['ruta_entrada'] = directorio
            self.requisitos['ruta_salida'] = directorio
        else:
            self.requisitos['ruta_entrada'] = directorio + '/'
            self.requisitos['ruta_salida'] = directorio + '/'
        # Define el nombre del archivo de salida 
        aux:str = ""
        for palabra in palabras:
            aux = aux + f"_{palabra}"
        self.requisitos['titulo'] = f"resultado_de_buscar{aux.upper()}"

	# Inicia el proceso de encontrar ocurrencias
        self.realizar_busqueda(palabras)  
          
    
    # Método que realiza la búsqueda
    # Recibe como argumento una cantidad variable de palabras
    def realizar_busqueda(self, palabras:str) -> None:
        if len(self.requisitos) != 3:
            print(' ✖ Aun no se han ingresado los datos necesarios.\n')
            return
        else:
            inicio = timeit.default_timer()
            b = self.Buscador(
                self.requisitos['ruta_entrada'],
                self.requisitos['titulo'],
                self.requisitos['ruta_salida'])
            b.encontrar(palabras)
            del b
            print(f"Duración de la búsqueda: {round(timeit.default_timer() - inicio,2)} segundos")
            
    
    class Buscador:
        """
        Se encarga de obtener los resultados y exportarlos
        a la misma carpeta donde se efectuó la búsqueda. 
        """      
        # Directorio de búsqueda
        _ruta_entrada:str
        # Referencia para el título del archivo con los resultados 
        _titulo:str
        # Directorio donde se escribira el archivo de salida    
        _ruta_salida:str
        # Resultado de la búsqueda
        _resultado:str
        
        def __init__(
                self,
                ruta_entrada:str,
                titulo:str,
                ruta_salida:str):
            
            self._ruta_entrada = ruta_entrada
            self._titulo = titulo
            self._ruta_salida = ruta_salida
            self._resultado = ''
    
        # Métodos de acceso y modificación de atributos
        def entrada(self) -> str:
            return self._ruta_entrada            
    
        def salida(self) -> str:
            return self._ruta_salida
    
        def titulo(self) -> str:
            return self._titulo
      
        def restablecer_valores(self) -> None:
            self._ruta_entrada = ''
            self._titulo = ''
            self._ruta_salida = ''
            self._resultado = ''
    
        def resultado(self) -> str:
            return self._resultado
    
        def encontrar(self, palabras:tuple[str]):
            if self.entrada() == '':
                print(' ✖ Aun no se ha ingresado una ruta de entrada.\n')
                return
            # Se genera la lista de documentos
            directorio = self.Directorio()
            lista_aux:list[str] = []
            lista_docs = directorio.listar_documentos(self.entrada(),lista_aux)
            del lista_aux
            del directorio
            # Se obtienen las ocurrencias en cada archivo
            for doc in lista_docs:
                titulo = doc[doc.rfind('/') + 1:]
                documento = self.Documento(doc)
                documento.buscar_ocurrencias(palabras)
                res:tuple[[int, str]] = documento.ocurrencias()
                del documento
                if len(res) == 0:
                    print(f" ✖  No hubo resultados en: {titulo}\n\n")
                # Se agregan al resultado final
                else:
                    self.incluir_resultados(res, doc)
                    print(f" ✔ {len(res)} ocurrencias en: {titulo}\n\n")
                del res
            del lista_docs
            # Se escribe el resultado en un txt en la ruta de salida 
            self.exportar_resultados()
    
    
        # Formatea las ocurrencias y las incluye al resultado final        
        def incluir_resultados(
                self,
                resultados:tuple[[int, str]],
                doc:str) -> None:
            c_aux1:str = f"\n\n\n 🞒 Documento: {doc}\n\n"
            for ocurrencia in resultados:
                c_aux1 += f"Pág. {ocurrencia[0]}: {ocurrencia[1]}\n\n"
            self._resultado += c_aux1
            del c_aux1
    
    
        # Escribe el txt final
        def exportar_resultados(self) -> None:
            print(f' ✔ Búsqueda finalizada.\n')
            b_aux1:bool = self.salida() != ''
            b_aux2:bool = self.titulo() != ''
            es_exportable:bool = b_aux1 and b_aux2
            if self.resultado() != '':  
                if es_exportable:
                    try:
                        ruta_final: str = f'{self.salida()}{self.titulo()}.txt'
                        escritura = open(ruta_final, "w", encoding="utf-8")                             
                        escritura.write(self.resultado())
                        escritura.close()
                        self.restablecer_valores()
                        #print(f' ✔ Búsqueda finalizada.\n')
                        print(f'El resultado se exportó al archivo: {ruta_final}\n\n')
                    except:
                        print(' ✖  Revisar los valores ingresados \n\n')
                        return
                else:
                    print(' ✖  Ingresar título y/o ruta de salida \n\n')
            else:
                print('No hubo coincidencias. Nada para exportar.\n')
                
    
        class Directorio:
            """
            Se encarga de construir la lista de PDFs en los cuales
            se efectuará la búsqueda.
            """
            # Recibe como argumento la ruta principal (recursiva)
            def listar_documentos(
                    self,
                    carpeta:str,
                    lista_docs:list[str]) -> list[str]:
        
                # Agrega la barra para prevenir errores
                if not carpeta.endswith('/'):
                    carpeta = carpeta + '/'
                ruta = Path(carpeta)
        
                # Construye la lista de archivos existentes en carpeta actual
                try:
                    lista_archivos:list[str] = [archivo.name for archivo
                                                in ruta.iterdir()]
                except:
                    print(' ✖ Revisar la ruta de salida ingresada.\n')
                    return
        
                for archivo in lista_archivos:
                    aux_1:bool = Path(ruta / f"{archivo}").is_file()
                    aux_2:bool = archivo.endswith('.pdf')
                    es_documento:bool =  aux_1 and aux_2
                    if es_documento:
                        lista_docs.append(carpeta + archivo)
                    # El archivo es una carpeta
                    elif Path(ruta / f"{archivo}").is_dir():
                        self.listar_documentos(f"{carpeta}{archivo}/", lista_docs)
        
                del lista_archivos
                return lista_docs
                        
        
        class Documento:
            """
            Se encarga de buscar en cada archivo pdf las posibles ocurrencias y
            de corregir las oraciones extraídas.
            """
            _ruta:str
            _ocurrencias:list[tuple[int, str]]
        
            def __init__(self, ruta):
                self._ruta = ruta
                self._ocurrencias = []
        
            def ruta(self) -> str:
                return self._ruta
        
            def agregar_ocurrencia(self, ocurrencia:tuple[int, str]) -> None:
                self._ocurrencias.append(ocurrencia)
        
            def ocurrencias(self) -> list[tuple[int, str]]:
                return self._ocurrencias
        
            def buscar_ocurrencias(self, palabras:tuple[str]) -> None:
                try:
                    with fitz.open(self.ruta()) as documento:
                        nro_pag:int = 1
                        for pagina in documento:        
                            # Obtiene el texto de cada página
                            contenido:str = pagina.get_text("text")
                            oraciones: list[str] = contenido.split('.')
        
                            # Verifica las ocurrencias en cada oración
                            for oracion in oraciones:
                                oracion = self.corregir(oracion)
                                contador:int = 0                        
                                for palabra in palabras:
                                    if palabra in oracion:
                                        contador += 1
                                    else:
                                        break
                                # Deben aparecer todas las palabras
                                if contador == len(palabras):
                                    tupla_aux:tuple[int, str] = (nro_pag, oracion)
                                    self.agregar_ocurrencia(tupla_aux)     
                            nro_pag += 1
                        return
                except:
                    print(f" ✖ No se pudo abrir {self.ruta()}\n")
                    return
        
            # Corrige espacios en blanco, saltos de línea, etc.
            # Acá agrego nuevas correciones a errores comunes.
            def corregir(self, oracion:str) -> str:        
                    oracion = oracion.replace('\n', ' ')
                    oracion = oracion.replace('  ', ' ')
                    oracion = oracion.replace('´ a','á')
                    oracion = oracion.replace('´ e','é')
                    oracion = oracion.replace('ı','i')
                    oracion = oracion.replace('´ i','í')
                    oracion = oracion.replace('´ o','ó')
                    oracion = oracion.replace('´ u','ú')
                    return oracion


if __name__ == "__main__":
    # Creo el analizador de argumentos
    analizador = argparse.ArgumentParser(description="Programa que busca ocurrencias de palabras en PDFs")

    # Tomo el primer argumento por separado
    analizador.add_argument("carpeta", help="Ubicación de los PDFs en los que se buscarán las palabras")
    
    # Acepto una cantidad arbitraria de palabras a buscar (mínimo una)
    analizador.add_argument("palabras", nargs='+', help="Lista de palabras a buscar en una oración")
    
    # Analiza los argumentos recibidos
    args = analizador.parse_args()
    
    # Llama a la función que instancia la búsqueda
    buscar(args.carpeta, args.palabras)      
