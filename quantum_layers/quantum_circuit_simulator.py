"""
QUANTUM CIRCUIT SIMULATION
- Qiskit ile quantum amplitude forecasting örneği
"""
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, transpile
from qiskit.visualization import plot_histogram
import numpy as np

class QuantumCircuitSimulator:
    def predict(self, prices: list):
        # Price normalization
        x = np.array(prices[-8:]) / np.max(prices[-8:])
        qr = QuantumRegister(3)
        cr = ClassicalRegister(3)
        qc = QuantumCircuit(qr, cr)
        qc.initialize(x, qr)
        for i in range(3):
            qc.h(qr[i])
        qc.measure(qr, cr)
        sim = Aer.get_backend("qasm_simulator")
        job = sim.run(transpile(qc, sim), shots=512)
        result = job.result().get_counts()
        # En çok çıkan state'i tahmin olarak dön
        likely = max(result, key=result.get)
        pred = int(likely, 2) / 8
        return pred
