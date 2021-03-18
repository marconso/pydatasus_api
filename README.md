# Pydatasus API

## Guia rápido de como usar essa bela API


### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010"

ou

### python pydatasus.py -d "SIM" -b "Óbito Fetal" -e "Acre" -a "2010, 2011, 2012"

## Usando com um import

```
# importando a biblioteca
import pydatasus

# instanciando a classe PyDatasus
datasus = PyDatasus()

# usando a função get_data() do objeto datasus
# "SIM" = Banco de dados
# "DO" = Base de dados (Óbito)
# "AC" = Sigla representativa do Acre
# "2010" = Ano de busca (pode ser passado uma lista contendo strings)
# exemplo:

    - usando string '2010'
    datasus.get_data('SIM', 'DO', 'AC', '2010')

### ou

    - usando uma lista de strins ['2010', '2011']
    datasus.get_data('SIM', 'DO', 'AC', ['2010', '2011'])
```


Mantenedor:

email: marconsodehsfilho@gmail.com

email: rodriguesmsb@gmail.com
