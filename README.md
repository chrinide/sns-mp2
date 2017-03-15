Input File Example
------------------

    import psi4nnmp2  # required
    
    molecule {
    0 1
    C 1.31865000 1.24752700 2.83170400
    C 2.13801100 0.22804800 2.03597400
    H 0.40147400 1.51578800 2.28085700
    H 1.90803500 2.16430200 3.00128900
    H 1.03119900 0.82800000 3.81046800
    H 1.54862600 -0.68872700 1.86639200
    H 2.42546100 0.64757600 1.05721100
    H 3.05518600 -0.04021300 2.58682200
    --
    0 1
    C 0.68390400 2.35566100 -0.86482800
    C 1.42861100 3.43933400 -0.08064700
    H 1.31969300 1.96524600 -1.67720400
    H -0.23838800 2.76826300 -1.30725700
    H 0.41122000 1.51976500 -0.19884700
    H 2.35090400 3.02673200 0.36178400
    H 1.70129500 4.27523200 -0.74662600
    H 0.79282300 3.82975100 0.73173200
    
    symmetry c1
    no_com
    no_reorient
    }
    
    set {
      memory 7gb
    }
    
    energy('nnmp2')


Testing
-------

From the git checkout, to test against a garden version, use

    pytest --psi4nnmp2_version psi4nnmp2/0.1.0/bin

To test against the local version in the checkout, before installing, use

    pytest --psi4nnmp2_version local