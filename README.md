# Pydatasus API

## Guia rápido de como usar essa bela API


### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010"

ou

### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010, 2011, 2012"

## Usando com um import

`
####### importando o arquivo
import pydatasus

####### instanciando 
datasus = PyDatasus()

####### usando a função get_data()
####### 1 - "SIM" = Banco de dados do SIM
####### 2 - "DO" = Base de dados Óbito (lista de bases em: arquivo databases.json)
####### 3 - "AC" = Sigla do ACRE
####### 4 - "2010" = Ano de busca
datasus.get_data('SIM', 'DO', 'AC', '2010')
####### ou
datasus.get_data('SIM', 'DO', 'AC', ['2010', '2011'])
`

Mantenedor:

email: marconsodehsfilho@gmail.com

email: rodriguesmsb@gmail.com
