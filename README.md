# Horario a iCalendar

Esta herramienta hecha en python permite exportar horarios de la [ESIIAB](https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2) a formato **.ics**, lo que permite tener un horario completo de cualquier curso y grupo en tu calendario.


# Ejecución - Automática

## Ejecutar run.bat
`run.bat` es una lista de instrucciones que instala automáticamente python si no está instalado, crea un entorno virutal donde seguidamente instala las dependencias y finalmente ejecuta `main.py`.

# Ejecución - Manual
## Clonar repositorio
[Instrucciones sobre cómo clonar un repositorio](https://docs.github.com/es/repositories/creating-and-managing-repositories/cloning-a-repository)
## instalar dependencias:    
`pip install -r requirements.txt`

## Ejecutar main.py
`python main.py`

# Cómo se usa?
![image](https://github.com/user-attachments/assets/4fea4a76-1034-4e3c-9e0c-5f5fded208ad)
Usando las flechas seleccionar la opción y presionar Enter

## Exportar archivo
Se genera un archivo con esta pinta "**3º GRUPO I (12).ics**". Importa el archivo a google calendar o pásatelo al móvil y ábrelo para tener en tu calendario todas tus asignaturas.

# Progreso
## TODO
- [ ] Obtener automáticamente la fecha de fin de semestre de acuerdo al semestre actual.
- [ ] Obtener automáticamente los horarios correspondientes al año actual.
- [ ] Obtener automáticamente los horarios correspondientes al semestre actual.
- [ ] Testear si run.bat instala correctamente python.


## DONE
- [x] Añadir una interfaz gráfica.
- [X] Automatizar la extracción de horarios.
- [X] Añadir run.bat 
