import numpy as np
from numpy import genfromtxt
from scipy import stats
from scipy import integrate
from scipy import signal
import matplotlib.pyplot as plt
import csv


#GEBERAR BITS (USAR EL .CSV)
# Número de bits
N = 10000

# Variable aleatoria binaria equiprobable
file1 = "bits10k.csv"
bits = np.genfromtxt(file1, delimiter=',')
#print(bits[0:10])

################################
#GENERAR MODELACION BPSK

# Frecuencia de operación
f = 5000 # Hz

# Duración del período de cada símbolo (onda)
T = 1/f # 1 ms

# Número de puntos de muestreo por período
p = 50

# Puntos de muestreo para cada período
tp = np.linspace(0, T, p)

# Creación de la forma de onda de la portadora
sinus = np.sin(2*np.pi * f * tp)

# Visualización de la forma de onda de la portadora
plt.plot(tp, sinus)
plt.xlabel("Tiempo / s")
plt.ylabel("Amplitud")
plt.title("Onda portadora")
plt.ticklabel_format(axis = "x", style = "sci", scilimits=(0,0))
plt.savefig("onda_portadora.png")
plt.show()

# Frecuencia de muestreo
fs = p/T # 50 kHz

# Creación de la línea temporal para toda la señal Tx
t = np.linspace(0, N*T, N*p)

# Inicializar el vector de la señal modulada Tx
senal = np.zeros(t.shape)

# Creación de la señal modulada OOK
for k, b in enumerate(bits):
    if b == 1:
        senal[k*p:(k+1)*p] = b * sinus
    else:
        senal[k*p:(k+1)*p] = -1 * sinus

# Visualización de los primeros bits modulados
pb = 10
tpp = np.linspace(0, pb*T, pb*p)
plt.figure()
plt.plot(tpp, senal[0:pb*p])
plt.xlabel("Tiempo / s")
plt.ylabel("Amplitud")
plt.title("Primeros periodos de la señal modulada según pb = 10")
plt.ticklabel_format(axis = "x", style = "sci", scilimits=(0,0))
plt.savefig("tx.png")
plt.show()

####################################
#CALCULO DE LA POTENCIA

# Potencia instantánea
Pinst = senal**2

# Potencia promedio a partir de la potencia instantánea (W)
Ps = integrate.trapz(Pinst, t) / (N * T)

print("La potencia promedio calculada es ", Ps)

#####################################
#DENSIDAD ESPECTRAL ANTES DEL CANAL RUIDOSO
fw, PSD = signal.welch(senal, fs)
plt.figure()
plt.semilogy(fw, PSD)
plt.xlabel('Frecuencia / Hz')
plt.ylabel('Densidad espectral de potencia / V**2/Hz')
plt.title("Densidad espectral antes de aplicar el canal ruidoso")
plt.savefig("bef_ruido.png")
plt.show()
plt.close()

####################################3
#SIMULACIÓN DEL CANAL

# Relación señal-a-ruido deseada
SNRrange = [-2,-1,0,1,2,3]
BER = []

for SNR in SNRrange:
    # Potencia del ruido para SNR y potencia de la señal dadas
    Pn = Ps / (10**(SNR / 10))

    # Desviación estándar del ruido
    sigma = np.sqrt(Pn)

    # Crear ruido (Pn = sigma^2)
    ruido = np.random.normal(0, sigma, senal.shape)

    # Simular "el canal": señal recibida
    Rx = senal + ruido

    # Visualización de los primeros bits recibidos
    plt.figure()
    plt.plot(tpp, Rx[0:pb*p])
    plt.xlabel("Tiempo / s")
    plt.ylabel("Amplitud")
    plt.title("Visualización de los primeros bits recibidos con SNR = " + str(SNR))
    plt.ticklabel_format(axis = "x", style = "sci", scilimits=(0,0))
    plt.savefig("rx" + str(SNR) + ".png")
    plt.show()
    plt.close()


    #########################################
    #DEMODUACIÓN Y DECODIFICACIÓN DE LA SEÑAL

    Es = np.sum(sinus**2)

    # Inicialización del vector de bits recibidos
    bitsRx = np.zeros(bits.shape)

    # Decodificación de la señal por detección de energía
    for k, b in enumerate(bits):
        Ep = np.sum(Rx[k*p:(k+1)*p] * sinus)
        if Ep > Es/2:
            bitsRx[k] = 1
        else:
            bitsRx[k] = 0

    err = np.sum(np.abs(bits - bitsRx))
    BER.append(err/N)

    print('Hay un total de {} errores en {} bits para una tasa de error de {}, para un SNR = {}.'.format(err, N, err/N,SNR))

    #############################
    #DENSIDAD ESPECTRAL DE LA POTENCIA
    # Después del canal ruidoso
    fw, PSD = signal.welch(Rx, fs)
    plt.figure()
    plt.semilogy(fw, PSD)
    plt.xlabel('Frecuencia / Hz')
    plt.ylabel('Densidad espectral de potencia / V**2/Hz')
    plt.title("Densidad espectral de la potencia (SNR="+str(SNR)+")")
    plt.savefig("den_espectral"+str(SNR)+".png")
    plt.show()
    plt.close()


####################
#GRÁFICA DE ERROR

plt.figure()
plt.scatter(SNRrange, BER)
plt.xlabel("SNR (dB)")
plt.ylabel("BER")
plt.title("BER VS SNR")
plt.savefig("BvsS.png")
plt.show()
plt.close()