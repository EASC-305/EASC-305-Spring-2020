#!/usr/bin/env python3

import numpy as np

def spectrogram(x, fs=1.0, t_out="time", norm=False, nperseg=5000, noverlap=4000,  nfft=5000):
    """ Wrapper for `scipy.signal.spectrogram`

        Compute the spectrogram analgous to the MATLAB style output.

        Parameters
        ----------
        x : array_like
            Timeseries of measurement values
        t_out: string, optional
            Return the t vector (x-axis of pcolormesh) as time ("time") or
            as sample number ("sample").
        fs : float, optional
            Sampling frequency of the `x` time series. Defaults to 1.0.
        norm: bool, optional
            Normalize the frequency. Scaled b/w 0 and 1 w/ units of ($\pi$rad/sample)
        nperseg: int, optional
            Length of each segment. Default is 5000.
            See `scipy.signal.spectrogram` for more details.
        noverlap: int, optional
            Number of points to overlap between segments. Default is 4000.
            See `scipy.signal.spectrogram` for more details.
        nfft: int, optional
            Length of the FFT used, if a zero padded FFT is desired. Defeault is 5000.
            See `scipy.signal.spectrogram` for more details.

        Returns
        -------
        f : ndarray
            Array of sample frequencies.
        t : ndarray
            Array of segment times (if t_out is "time") or sample number (if t_out is "sample")
        Sxx: ndarray
            Spectrogram of x. In units of power.

        Examples
        --------
        >>> from scipy import signal
        >>> import matplotlib.pyplot as plt

        Generate a test signal, a 2 Vrms sine wave whose frequency is slowly
        modulated around 3kHz, corrupted by white noise of exponentially
        decreasing magnitude sampled at 10 kHz.
        (^^^^ This a very complicated way to generate a signal, but we are following
        the example from "scipy.signal.spectrogram" )

        >>> fs = 10e3
        >>> N = 1e5
        >>> amp = 2 * np.sqrt(2)
        >>> noise_power = 0.01 * fs / 2
        >>> time = np.arange(N) / float(fs)
        >>> mod = 500*np.cos(2*np.pi*0.25*time)
        >>> carrier = amp * np.sin(2*np.pi*3e3*time + mod)
        >>> noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
        >>> noise *= np.exp(-time/5)
        >>> x = carrier + noise

        Compute and plot the spectrogram.

        >>> f, t, Sxx = spectrogram(x, fs)
        >>> plt.pcolormesh(t, f, Sxx, shading='gouraud')
        >>> # This y-axis label assumes "norm=False"
        >>> plt.ylabel('Frequency [Hz]')
        >>> # This x-axis t assumes "t_out=time"
        >>> plt.xlabel('Time')
        >>> # This colorbar label assumes "norm=False"
        >>> plt.colorbar(label='Power (dB)')
    """
    import scipy.signal as signal

    # Make sure that the "t_out" variable is passed
    if t_out not in ["time", "sample"]:
        raise ValueError('unknown value for t_out {}, must be one of {}'
                         .format(t_out, ["time", "sample"]))

    # Calculate the spectrogram with scipy.signal
    f, t, Sxx = signal.spectrogram(x, fs=fs,
                                   nperseg=nperseg,
                                   noverlap=noverlap,
                                   nfft=nfft,
                                   scaling='spectrum'
                                   )
    # Convert the spectrogram from scipy default to power in dB
    Sxx = 10*np.log10(Sxx)
    # Normalize frequency if kwarg passed
    if norm == True:
        f /= np.max(f)
    # Let's check how the time data should be returned
    if t_out == "sample":
        t = np.linspace(0, t[-1] / dt, t.shape[0])

    return f, t, Sxx
