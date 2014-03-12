File
{
    Grid    = "demo_msh.tdr"
    Plot    = "demo"
    Current = "demo"
    Output  = "demo"
}

Electrode
{
    { Name="substrate"      Voltage=0.0}
    { Name="source"         Voltage=0.0}
    { Name="drain"          Voltage=0.0}
    { Name="gate1"          Voltage=0       WorkFunction=4.1}
    { Name="gate2"          Voltage=0       WorkFunction=4.1}
    { Name="gate3"          Voltage=0       WorkFunction=4.1}
}

Physics
{
    Mobility( DopingDep HighFieldSat Enormal )
    EffectiveIntrinsicDensity( OldSlotboom )
    Recombination( SRH(DopingDep) )
}

*Physcis (RegionInterface = "")
*{
*   Traps (FixedCharge Conc=)
*}

Math
{
    Extrapolate
    Method=PARDISO
    Iterations=12
    Digits=5
}

CurrentPlot
{
    Potential
    (
        Average(RegionInterface="R.subs/R.gate2.gr1")
        Average(RegionInterface="R.subs/R.gate2.gr2")
        Average(RegionInterface="R.subs/R.gate2.gr3")
    )
    eQuasiFermiEnergy
    (
        Average(RegionInterface="R.subs/R.gate2.gr1")
        Average(RegionInterface="R.subs/R.gate2.gr2")
        Average(RegionInterface="R.subs/R.gate2.gr3")
        (0.12, -1e-6)
    )
    ConductionBandEnergy
    (
        Average(RegionInterface="R.subs/R.gate2.gr1")
        Average(RegionInterface="R.subs/R.gate2.gr2")
        Average(RegionInterface="R.subs/R.gate2.gr3")
        (0.12, -1e-6)
    )
}

Solve
{
    Coupled ( Iterations=50 ) { Poisson }
    Coupled { Poisson Electron Hole }
    
    Quasistationary
    (
        InitialStep=1e-3        Increment=1.6
        MinStep=1e-5            MaxStep=0.2
        Goal{ Name="gate1"      Voltage=10}
    ){ Coupled { Poisson } 
       CurrentPlot ( Time=(-1)) }

    Quasistationary
    (
        InitialStep=1e-3        Increment=1.6
        MinStep=1e-5            MaxStep=0.2
        Goal{ Name="gate3"      Voltage=10}
    ){ Coupled { Poisson }
       CurrentPlot ( Time=(-1) ) }

    Quasistationary
    (
        InitialStep=1e-3        Increment=1.6       Decrement=4
        MinStep=1e-5            MaxStep = 0.2
        Goal{ Name="drain"      Voltage=1.5}
    ){ Coupled { Poisson Electron Hole }
       CurrentPlot ( Time=(-1)) }

    NewCurrentPrefix="pos_"
    Quasistationary
    (
        InitialStep=1e-3        Increment=1.6       Decrement=4
        MinStep=1e-5            MaxStep = 0.2
        Goal{ Name="gate2"      Voltage=16}
    ){ Coupled { Poisson Electron Hole }
       CurrentPlot ( Time=(1) ) }
}

Plot
{
    *-Carrier Densities:
    eDensity hDensity

    *-Currents and current components:
    Current/Vector eCurrent/Vector hCurrent/Vector
    eMobility hMobility
    eVelocity hVelocity

    *-Fields, Potentials and Charge distributions
    ElectricField/Vector 
    Potential 
    eQuasiFermiPotential hQuasiFermiPotential eQuasiFermiEnergy hQuasiFermiEnergy
    SpaceCharge

    *-Driving forces
    eGradQuasiFermi/Vector hGradQuasiFermi/Vector
    eEparallel hEparallel 
    eENormal hENormal

    *-Temperatures
    *LatticeTemperature
    *eTemperature hTemperature

    *-Generation/Recombination
    *SRHRecombination
    *AvalancheGeneration eAvalancheGeneration hAvalancheGeneration
    *TotalRecombination

    *-Doping Profiles
    *Doping 
    *DonorConcentration AcceptorConcentration

    *-Band structure
    BandGap 
    BandGapNarrowing
    ElectronAffinity
    ConductionBandEnergy ValenceBand

    *-Traps
    eTrappedCharge hTrappedCharge
    eInterfaceTrappedCharge hInterfaceTrappedCharge

    *-Gate Tunneling/Hot carrier injection
    * FowlerNordheim 
    * HotElectronInjection HotHoleInjection

    *-Tunneling
    * BarrierTunneling eBarrierTunneling hBarrierTunneling
    * eDirectTunnel hDirectTunnel

}
