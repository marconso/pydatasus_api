# Pydatasus API

## Guia rápido de como usar essa bela API


### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010"

ou

### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010, 2011, 2012"

## Usando com um import

`
import pydatasus

datasus = PyDatasus()

datasus.get_data('SIM', 'DO', 'AC', '2010')
### ou
datasus.get_data('SIM', 'DO', 'AC', ['2010', '2011'])
`

Mantenedor:

email: marconsodehsfilho@gmail.com

email: rodriguesmsb@gmail.com
