import numpy as np
from parameters import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
from iirfilter import *
from prn_generator import *
from integrator import *
from peak_finder import *
from squaring_loop import *
from clock_recovery import *

USE_COSTAS_LOOP = False

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

i_early_integrator = Integrator()
q_early_integrator = Integrator()
i_late_integrator = Integrator()
q_late_integrator = Integrator()

seq_len_samplerate = DATA_BITRATE * CHIP_RATE / SEQ_LEN
# make this filter 1/4 of sequence frequency (filter for the dsss track)
# error_filt = IIRFilter(1/16)
# dummy_integrator = Integrator()

dummy2 = 0
dummy2plot = []

dummy3 = 0
dummy3plot = []
dummy4 = 0

derivator = Derivator()
# end variables for tracking

# variables for costas loop
costas_cutoff_frac = 4 * (CHIP_RATE * DATA_BITRATE) / CARRIER_SAMPLERATE
# loop_filter = IIRFilter(1/10)
costas_i_filter = IIRFilter(costas_cutoff_frac)
costas_q_filter = IIRFilter(costas_cutoff_frac)

squaring_loop = SquaringLoop(CARRIER_SAMPLERATE, RX_CARRIER_CENTER, PLL_MAX_DEVIATION)

# end variables for costas loop
prng.advancePhaseSamples(-43112)

# variables for alignment peak detector
peak_finder = PeakFinder(SEQ_LEN, PEAK_FINDER_MIN_ABOVE_AVERAGE)


# end vars for alignment peak detector

# vars for data clock recovery
edge_det = Derivator()
clock_recovery_pll = ClockPLL2(CARRIER_SAMPLERATE, DATA_BITRATE, 10)
clock_recovery_loop_correction = 0
output_bits = []
# end vars for data clock recovery

for i in range(len(times)):
    # giant loop
    t = times[i]

    input = data[i]
    LO_i = np.cos(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t)
    LO_q = np.sin(2 * np.pi * (RX_CARRIER_CENTER + loop_correction) * t)

    # costas loop
    if USE_COSTAS_LOOP:
        i_sig_filtered = costas_i_filter.pushValue(i_sig)
        q_sig_filtered = costas_q_filter.pushValue(q_sig)

        constellation_error = (i_sig_filtered * q_sig_filtered)  # no loop filter required! (apart from an integrator)
        # apply scaling function (makes loop converge faster)
        constellation_error = np.arctan(constellation_error)
        # loop filter (integrator)
        loop_correction += -0.0002 * constellation_error
        # loop_correction += -0.00005 * constellation_error
        # end of costas loop demodulator
    else:
        loop_correction = squaring_loop.update(input, LO_i)
        #loop_correction = squaring_loop.loop_correction


    i_sig = (data[i] * LO_i)
    q_sig = (data[i] * LO_q)

    prn = (prng.getSample0() - 0.5) * 2
    prng.advancePhase()

    despread_i = i_filt.pushValue(i_sig * prn)
    despread_q = q_filt.pushValue(q_sig * prn)

    demodulated = 0

    if receiver_state == RX_STATE_ACQ:
        # acquire

        i_integrator.accumulate(despread_i * despread_i)
        q_integrator.accumulate(despread_q * despread_q)

        if i % (samples_per_chip * SEQ_LEN) == 0:
            i_integral = i_integrator.dumpValue()
            q_integral = q_integrator.dumpValue()
            correlation_energy = i_integral + q_integral
            print(f"correlation energy: {correlation_energy}")

            # this is a dynamic threshold later
            found, delta_halfPeriods = peak_finder.pushValue(correlation_energy)

            if found:
                # alignment found, now scroll back to it
                prng.advancePhaseNHalfPeriods(delta_halfPeriods)
                receiver_state = RX_STATE_TRACK
                print(f"FOUND!!!!!!!!!!!!!!!!! {peak_finder.max_val}, dummy4 = {dummy4}, delta = {delta_halfPeriods}")
            else:
                prng.advancePhaseHalfPeriod()

    elif receiver_state == RX_STATE_TRACK:
        # track
        prn_early = (prng.getSample45() - 0.5) * 2
        prn_late = (prng.getSampleMinus45() - 0.5) * 2
        prn_aligned = (prng.getSample0() - 0.5) * 2

        i_early_despread = i_early_filt.pushValue(i_sig * prn_early)
        q_early_despread = i_early_filt.pushValue(q_sig * prn_early)
        i_late_despread = i_late_filt.pushValue(i_sig * prn_late)
        q_late_despread = i_late_filt.pushValue(q_sig * prn_late)
        demodulated = despread_i

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

            alignment_error = (alignment_error_raw)

            d_term = derivator.pushValue(alignment_error)

            error_output = -(0.015 * alignment_error + 0.001 * d_term)

            MAX_ERROR_OUT = 0.8
            if np.abs(error_output) > MAX_ERROR_OUT:
                error_output = error_output * MAX_ERROR_OUT / np.abs(error_output)

            prng.advancePhaseSamples(error_output)

            print(f"alignment error: {error_output}")

        data_bit = np.sign(demodulated)



        # clock recovery system
        edges = np.abs(edge_det.pushValue(data_bit))
        clock_LO = np.cos(2 * np.pi * (DATA_BITRATE + clock_recovery_loop_correction) * t)
        clock_recovery_loop_correction = clock_recovery_pll.update(edges, clock_LO)


        if edges > 0:
            output_bits.append(int(data_bit / 2 + 1))

        dummy2 = clock_LO + 2.2

        dummy3 = data_bit
        dummy3 = clock_recovery_pll.dummy


    dummy2plot.append(dummy2)
    dummy3plot.append(dummy3)
    # output.append(demodulated * 10)
    outbits.append(clock_recovery_loop_correction)
    # baseband.append(dummy1)



output_bits = np.array(output_bits)
bitstring = ''.join(output_bits.astype(str))
print(bitstring)  # Output: "1011"
print("inverted:")
bitstring = ''.join((1 - output_bits).astype(str))
print(bitstring)
print(" ")
print("asd")
# plt.plot(abs(np.fft.rfft(baseband)))
# plt.plot(np.cos(2 * np.pi * CARRIER_CENTER * times))
plt.plot(baseband)
plt.plot(output)
plt.plot(outbits)
plt.plot(dummy2plot)
plt.plot(dummy3plot)
plt.show()