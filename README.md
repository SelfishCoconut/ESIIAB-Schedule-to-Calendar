# Horario a iCalendar

Esta herramienta hecha en python permite exportar horarios de la [ESIIAB](https://www.esiiab.uclm.es/grado/horarios.php?que=&curso=2024-25&submenu=2) a formato **.ics**, lo que permite tener un horario completo de cualquier curso y grupo en tu calendario.

# Cómo ejecutarlo
1. Clonar repositorio
2. Instalar dependencias:  
`pip install -r requirements.txt`
## instalar dependencias:  
`pip install selenium`

## Modificar variables: 
```
course: str = '3º'  
group: str = "GRUPO I" 
```  
Cambiar de acuerdo al curso y grupo

## Ejecutar main.py
`python main.py`
