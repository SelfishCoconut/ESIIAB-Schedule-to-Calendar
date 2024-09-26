# Horario a iCalendar

Esta herramienta hecha en python permite exportar horarios de la [ESIIAB](https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2) a formato **.ics**, lo que permite tener un horario completo de cualquier curso y grupo en tu calendario.

# Cómo ejecutarlo
## Clonar repositorio
[Instrucciones sobre cómo clonar un repositorio](https://docs.github.com/es/repositories/creating-and-managing-repositories/cloning-a-repository)
## instalar dependencias:    
`pip install -r requirements.txt`

## Modificar variables: 
```
course: str = '3º'  
group: str = "GRUPO I" 
```  
Cambiar de acuerdo al curso y grupo

## Ejecutar main.py
`python main.py`
