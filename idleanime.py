import random

options = ['335','481','383','634','513']

# o bot precisa tomar decis�es a cada X tempo
# op��es de decis�es de macro level:
# come�ar anime novo, assistir epis�dio de um anime do watching,
# dropar anime, pausar anime, despausar anime, desdropar anime,
# postar uma atividade, adicionar algo nos favoritos

# tomada de decis�o:
# delay: 30 minutos, a menos que esteja assistindo algo
# neste caso empurra a decis�o para 5 minutos ap�s finalizar
#