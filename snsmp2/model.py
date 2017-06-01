import os
import numpy as np
from scipy.optimize import brentq
from scipy.stats import laplace, rv_continuous

from psi4 import core

HARTREE2KCAL = 627.509474
KCAL2MEH = 1.0 / (HARTREE2KCAL / 1000.)


def prepare_input_vector(input_fields):
    field_order = [
        'DF-HF/desavtz CP Interaction Energy',
        'DF-HF/desavqz CP Interaction Energy',
        'DF-HF/desavqz Electrostatic Interaction Energy',
        'DF-HF/desavqz Heitler-London Energy',
        'DF-HF/desavqz Density Matrix Overlap',
        'DF-MP2/desavtz CP Interaction Energy',
        'DF-MP2/desavtz CP Same-Spin Interaction Energy',
        'DF-MP2/desavqz CP Interaction Energy',
        'DF-MP2/desavqz Electrostatic Interaction Energy',
        'DF-MP2/desavqz Density Matrix Overlap',
        'DF-MP2/desavqz CP Same-Spin Interaction Energy',
        'SAPT DISP20 ENERGY',
        'SAPT SAME-SPIN DISP20 ENERGY',
        'SAPT ELST10,R ENERGY',
        'SAPT EXCH10 ENERGY',
        'SAPT EXCH10(S^2) ENERGY',
        'SAPT EXCH-DISP20 ENERGY',
        'SAPT SAME-SPIN EXCH-DISP20 ENERGY',
        'SAPT EXCH-IND20,R ENERGY',
        'SAPT IND20,R ENERGY',

        0,  # lo_zeta==2
        1,  # lo_zeta==3
    ]

    # Prepare x
    x = []
    for f in field_order:
        if isinstance(f, str):
            if f.upper().endswith('ENERGY'):
                x.append(HARTREE2KCAL * input_fields[f])
            else:
                x.append(input_fields[f])
        else:
            x.append(f)

    x = np.asarray(x)

    trip_lo = input_fields['DF-MP2/desavtz CP Same-Spin Interaction Energy']
    trip_hi = input_fields['DF-MP2/desavqz CP Same-Spin Interaction Energy']

    sing_lo = input_fields['DF-MP2/desavtz CP Interaction Energy'] - input_fields['DF-HF/desavtz CP Interaction Energy'] - trip_lo
    sing_hi = input_fields['DF-MP2/desavqz CP Interaction Energy'] - input_fields['DF-HF/desavqz CP Interaction Energy'] - trip_hi


    trip_cbs = ((trip_hi * (4**3)) - (trip_lo * (3**3))) / (4**3 - 3**3)
    sing_cbs = ((sing_hi * (4**3)) - (sing_lo * (3**3))) / (4**3 - 3**3)   
    hf_qz = input_fields['DF-HF/desavqz CP Interaction Energy']

    y = HARTREE2KCAL * np.asarray([hf_qz, trip_cbs, sing_cbs])

    return x, y



def sns_mp2_model(input_fields, n=10000, dropout=True, random_seed=0):
    core.tstart()
    core.print_out('''
//===================================================================================//

                                  SNS-MP2

    R. T. McGibbon, A. G. Taube, A. G. Donchev, K. Siva, F. Fernandez, C. Hargus,
      K.-H. Law, J.L. Klepeis, and D. E. Shaw. "Improving the accuracy of
      Moller-Plesset perturbation theory with neural networks"

//===================================================================================//


    SNS-MP2 Inputs
    --------------

    DF-HF/desavqz Density Matrix Overlap:                        {DF-HF/desavqz Density Matrix Overlap} [a.u.]
    DF-HF/desavqz Electrostatic Interaction Energy:              {DF-HF/desavqz Electrostatic Interaction Energy} [a.u.]
    DF-HF/desavqz Heitler-London Energy:                         {DF-HF/desavqz Heitler-London Energy} [a.u.]
    DF-MP2/desavqz Density Matrix Overlap:                       {DF-MP2/desavqz Density Matrix Overlap} [a.u.]
    DF-MP2/desavqz Electrostatic Interaction Energy:             {DF-MP2/desavqz Electrostatic Interaction Energy} [a.u.]
    SAPT DISP20 ENERGY:                                          {SAPT DISP20 ENERGY} [a.u.]
    SAPT ELST10,R ENERGY:                                        {SAPT ELST10,R ENERGY} [a.u.]
    SAPT EXCH-DISP20 ENERGY:                                     {SAPT EXCH-DISP20 ENERGY} [a.u.]
    SAPT EXCH-IND20,R ENERGY:                                    {SAPT EXCH-IND20,R ENERGY} [a.u.]
    SAPT EXCH10 ENERGY:                                          {SAPT EXCH10 ENERGY} [a.u.]
    SAPT EXCH10(S^2) ENERGY:                                     {SAPT EXCH10(S^2) ENERGY} [a.u.]
    SAPT HF TOTAL ENERGY:                                        {SAPT HF TOTAL ENERGY}[a.u.]
    SAPT IND20,R ENERGY:                                         {SAPT IND20,R ENERGY} [a.u.]
    SAPT SAME-SPIN DISP20 ENERGY:                                {SAPT SAME-SPIN DISP20 ENERGY} [a.u.]
    SAPT SAME-SPIN EXCH-DISP20 ENERGY:                           {SAPT SAME-SPIN EXCH-DISP20 ENERGY} [a.u.]
    DF-HF/desavqz CP Interaction Energy:                         {DF-HF/desavqz CP Interaction Energy} [a.u.]
    DF-HF/desavtz CP Interaction Energy:                         {DF-HF/desavtz CP Interaction Energy} [a.u.]
    DF-MP2/desavqz CP Interaction Energy:                        {DF-MP2/desavqz CP Interaction Energy} [a.u.]
    DF-MP2/desavqz CP Opposite-Spin Interaction Energy:          {DF-MP2/desavqz CP Opposite-Spin Interaction Energy} [a.u.]
    DF-MP2/desavqz CP Same-Spin Interaction Energy:              {DF-MP2/desavqz CP Same-Spin Interaction Energy} [a.u.]
    DF-MP2/desavtz CP Interaction Energy:                        {DF-MP2/desavtz CP Interaction Energy} [a.u.]
    DF-MP2/desavtz CP Opposite-Spin Interaction Energy:          {DF-MP2/desavtz CP Opposite-Spin Interaction Energy} [a.u.]
    DF-MP2/desavtz CP Same-Spin Interaction Energy:              {DF-MP2/desavtz CP Same-Spin Interaction Energy} [a.u.]
'''.format(**input_fields))


    random = np.random.RandomState(random_seed)
    input_nn_data, final_layer_data = prepare_input_vector(input_fields)

    f = np.load(os.path.join(os.path.dirname(__file__), 'weights.0061900.npz'))
    layers = [
        ('hidden_0', np.tanh, 0.025),
        ('hidden_1', np.tanh, 0.025),   
        ('hidden_2', np.tanh, 0.025),   
        ('hidden_3', np.tanh, 0.025),   
        ('hidden_4', np.tanh, 0.025),   
        ('hidden_5', np.tanh, 0.025),   
        ('hidden_6', np.tanh, 0.025),   
        ('hidden_7', np.tanh, 0.025),   
        ('hidden_8', np.tanh, 0.025),   
        ('hidden_9', np.tanh, 0.025),
        ('spin_coefficients', lambda x: np.log(1+np.exp(x)), 0),        
    ]
    
    output_data = np.tile(input_nn_data, [n, 1])
    for j, (name, activation, dropout_prob) in enumerate(layers):
        output_data = activation(np.dot(output_data, f['%s:%s_W' %(name, name)]) + f['%s:%s_b' % (name, name)])

        if dropout_prob > 0 and dropout is True:
            retain_prob = 1 - dropout_prob
            random_tensor = random.binomial(1, size=output_data.shape, p=retain_prob).astype(np.float64)
            output_data *= random_tensor
            output_data /= retain_prob

        if name == 'hidden_9':
            last_hidden_layer = np.copy(output_data)

    sns_mp2_energy = np.multiply(np.tile(final_layer_data, (n, 1)), np.hstack((np.ones((n,1)), output_data))).sum(axis=1)
    b_activation = lambda x: 0.000010 + np.log(1+np.exp(np.squeeze(x)))
    b = b_activation(np.dot(
        np.hstack((last_hidden_layer, sns_mp2_energy.reshape(n, 1))),
        f['b:b_W']) + f['b:b_b'])

    lm = laplace_mixture()
    lm._set_params(sns_mp2_energy, b)
    format_results(output_data, lm)
    core.tstop()

    return np.mean(sns_mp2_energy)


def format_results(spin_coefficients, laplace_mixture):
    def determine_predictive_interval(q=0.95):
        lm = laplace_mixture
        lower_bound = brentq(lambda x: lm.cdf(x) - (0.5 - q/2), a=lm.mean() - 3*np.max(lm._scales), b=lm.mean())
        upper_bound = brentq(lambda x: lm.cdf(x) - (0.5 + q/2), a=lm.mean(), b=lm.mean() + 3*np.max(lm._scales))
        return lower_bound, upper_bound

    lower_bound_kcal, upper_bound_kcal = determine_predictive_interval(q=0.95)
    mean_kcal = laplace_mixture.mean()


    core.print_out('''
    SNS-MP2 Spin Results
    --------------------

    SNS Same-Spin Scale                       {mean_trip_scale:10.8f}   [95% CI: {low_trip_scale:8.6f} -- {high_trip_scale:8.6f}]
    SNS Opposite-Spin Scale                   {mean_sing_scale:10.8f}   [95% CI: {low_sing_scale:8.6f} -- {high_sing_scale:8.6f}]

    SNS-MP2 Interaction Energy                {mean_meh:10.8f}   [95% CI: {lower_bound_meh:10.8f} -- {upper_bound_meh:10.8f}] [mEh]
                                              {mean_kcal:10.8f}   [95% CI: {lower_bound_kcal:10.8f} -- {upper_bound_kcal:10.8f}] [kcal/mol]

//===================================================================================//
'''.format(
    mean_trip_scale=np.mean(spin_coefficients, axis=1)[0],
    mean_sing_scale=np.mean(spin_coefficients, axis=1)[1],
    low_trip_scale=np.percentile(spin_coefficients, q=2.5, axis=1)[0],
    high_trip_scale=np.percentile(spin_coefficients, q=97.5, axis=1)[0],
    low_sing_scale=np.percentile(spin_coefficients, q=2.5, axis=1)[1],
    high_sing_scale=np.percentile(spin_coefficients, q=97.5, axis=1)[1],    

    # Outputs
    mean_kcal=mean_kcal,
    mean_meh=mean_kcal * KCAL2MEH,
    lower_bound_kcal=lower_bound_kcal,
    upper_bound_kcal=upper_bound_kcal,
    lower_bound_meh=lower_bound_kcal * KCAL2MEH,
    upper_bound_meh=upper_bound_kcal * KCAL2MEH))


class laplace_mixture(rv_continuous):
    def _set_params(self, locs, scales):
        self._locs = locs
        self._scales = scales
        self._laplaces = laplace(loc=locs, scale=scales)

    def _pdf(self, x):
        return np.mean(self._laplaces.pdf(x))
    def _cdf(self, x):
        return np.mean(self._laplaces.cdf(x))

    def mean(self):
        return self._locs.mean()