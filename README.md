# Horario a iCalendar

Esta herramienta hecha en python permite exportar horarios de la [ESIIAB](https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2) a formato **.ics**, lo que permite tener un horario completo de cualquier curso y grupo en tu calendario.

# Cómo ejecutarlo
## Clonar repositorio
[Instrucciones sobre cómo clonar un repositorio](https://docs.github.com/es/repositories/creating-and-managing-repositories/cloning-a-repository)
## instalar dependencias:    
`pip install -r requirements.txt`

## Modificar variables: 
En el archivo `main.py`
```
course: str = '3º'  
group: str = "GRUPO I" 
```  
Cambiar el contenido de las variables `course` y `group` de acuerdo al curso y grupo del que se quiere obtener el horario.

## Ejecutar main.py
`python main.py`

## Exportar archivo
Se genera un archivo con esta pinta "**3º GRUPO I (12).ics**". Importa el archivo a google calendar o pásatelo al móvil y ábrelo para tener en tu calendario todas tus asignaturas.

# Progreso
## TODO
- [ ] Añadir una interfaz gráfica.
- [ ] Obtener automáticamente la fecha de fin de semestre de acuerdo al semestre actual.
- [ ] Obtener automáticamente los horarios correspondientes al año actual.
- [ ] Obtener automáticamente los horarios correspondientes al semestre actual.

## DONE
- [X] Automatizar la extracción de horarios.
