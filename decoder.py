import numpy as np
from parameters import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
from iirfilter import *
from prn_generator import *
from integrator import *

samplerate, data = wavfile.read("output.wav")

duration = len(data) / samplerate

times = np.linspace(0, duration, len(data))

samples_per_chip = int(CARRIER_SAMPLERATE / (CHIP_RATE * DATA_BITRATE))

# Make this filter cutoff be 1 / chiprate
cutoff_frac = 1/CHIP_RATE * (CHIP_RATE * DATA_BITRATE) / (CARRIER_SAMPLERATE / 2)
print(cutoff_frac)

i_filt = IIRFilter(cutoff_frac)
q_filt = IIRFilter(cutoff_frac)


output = []
loop_correction = 0

baseband = []
outbits = []

prng = PRNG(CARRIER_SAMPLERATE, PRN_SEED, SEQ_LEN, DATA_BITRATE, CHIP_RATE)

i_integrator = Integrator()
q_integrator = Integrator()

dummy1 = 0

RX_STATE_ACQ = 0
RX_STATE_TRACK = 1

receiver_state = RX_STATE_ACQ
# variables for tracking
i_early_filt = IIRFilter(cutoff_frac)
q_early_filt = IIRFilter(cutoff_frac)
i_late_filt = IIRFilter(cutoff_frac)
q_late_filt = IIRFilter(cutoff_frac)

sig_out_filt = IIRFilter(cutoff_frac)

i_early_integrator = Integrator()
q_early_integrator = Integrator()
i_late_integrator = Integrator()
q_late_integrator = Integrator()

seq_len_samplerate = DATA_BITRATE * CHIP_RATE / SEQ_LEN
# make this filter 1/4 of sequence frequency
error_filt = IIRFilter(1/8)

dummy2 = 0
dummy2plot = []

derivator = Derivator()
# end variables for tracking

prng.advancePhaseSamples(-43112)

for i in range(len(times)):
    # giant loop
    t = times[i]

    input = data[i]

    i_sig = (data[i] * np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))
    q_sig = (data[i] * np.sin(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t))

    prn = (prng.getSample0() - 0.5) * 2
    prng.advancePhase()

    demodulated = 0

    if receiver_state == RX_STATE_ACQ:
        # acquire
        despread_i = i_filt.pushValue(i_sig * prn)
        despread_q = q_filt.pushValue(q_sig * prn)

        i_integrator.accumulate(despread_i * despread_i)
        q_integrator.accumulate(despread_q * despread_q)

        demodulated = despread_q

        if i % (samples_per_chip * SEQ_LEN) == 0:
            i_integral = i_integrator.dumpValue()
            q_integral = q_integrator.dumpValue()
            correlation_energy = i_integral + q_integral
            # print(correlation_energy)

            # this must be changed to a dynamic threshold later
            if correlation_energy > 400:
                # alignment found
                receiver_state = RX_STATE_TRACK


            prng.advancePhaseHalfPeriod()
            dummy1 = correlation_energy
    else:
        # track
        prn_early = (prng.getSample45() - 0.5) * 2
        prn_late = (prng.getSampleMinus45() - 0.5) * 2
        prn_aligned = (prng.getSample0() - 0.5) * 2

        i_early_despread = i_early_filt.pushValue(i_sig * prn_early)
        q_early_despread = i_early_filt.pushValue(q_sig * prn_early)
        i_late_despread = i_late_filt.pushValue(i_sig * prn_late)
        q_late_despread = i_late_filt.pushValue(q_sig * prn_late)
        demodulated = sig_out_filt.pushValue(i_sig * prn_aligned) * 20

        i_early_integrator.accumulate(i_early_despread * i_early_despread)
        q_early_integrator.accumulate(q_early_despread * q_early_despread)
        i_late_integrator.accumulate(i_late_despread * i_late_despread)
        q_late_integrator.accumulate(q_late_despread * q_late_despread)

        if i % (samples_per_chip * SEQ_LEN) == 0:
            i_early_integral = i_early_integrator.dumpValue()
            q_early_integral = q_early_integrator.dumpValue()
            i_late_integral = i_late_integrator.dumpValue()
            q_late_integral = q_late_integrator.dumpValue()

            correlation_energy_early = i_early_integral + q_early_integral
            correlation_energy_late = i_late_integral + q_late_integral

            alignment_error_raw = correlation_energy_late - correlation_energy_early
            alignment_error = error_filt.pushValue(alignment_error_raw) / 10

            d_term = derivator.pushValue(alignment_error)

            error_output = alignment_error # - 0.1 * d_term

            prng.advancePhaseSamples(error_output)

            dummy2 = d_term * 10
            dummy1 = alignment_error * 10
            print(f"alignment error: {alignment_error}")

    dummy2plot.append(dummy2)
    output.append(demodulated * 10)
    # outbits.append(despread_q)
    baseband.append(dummy1)



print(samplerate)

# plt.plot(abs(np.fft.rfft(baseband)))
# plt.plot(np.cos(2 * np.pi * CARRIER_CENTER * times))
plt.plot(baseband)
plt.plot(output)
plt.plot(outbits)
plt.plot(dummy2plot)
plt.show()

